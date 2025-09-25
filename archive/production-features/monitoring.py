"""Monitoring and metrics for Pipecat Agent Builder."""

import time
import asyncio
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict, deque
import json
from pathlib import Path

from core.logger import setup_logger

logger = setup_logger("monitoring")


@dataclass
class MetricPoint:
    """Individual metric measurement."""
    timestamp: float
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class BuildSession:
    """Track a complete agent building session."""
    session_id: str
    start_time: float
    end_time: Optional[float] = None
    agent_name: Optional[str] = None
    use_case: Optional[str] = None
    status: str = "in_progress"  # in_progress, completed, failed
    error_message: Optional[str] = None
    metrics: Dict[str, Any] = field(default_factory=dict)
    
    def duration(self) -> float:
        """Get session duration in seconds."""
        end = self.end_time or time.time()
        return end - self.start_time
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "start_time": self.start_time,
            "end_time": self.end_time,
            "agent_name": self.agent_name,
            "use_case": self.use_case,
            "status": self.status,
            "error_message": self.error_message,
            "duration": self.duration(),
            "metrics": self.metrics
        }


class MetricsCollector:
    """Collect and store application metrics."""
    
    def __init__(self, max_points: int = 1000):
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque(maxlen=max_points))
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.sessions: Dict[str, BuildSession] = {}
        self.start_time = time.time()
    
    def record_metric(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Record a metric point."""
        point = MetricPoint(
            timestamp=time.time(),
            value=value,
            labels=labels or {}
        )
        self.metrics[name].append(point)
        logger.debug(f"Recorded metric {name}: {value}")
    
    def increment_counter(self, name: str, labels: Optional[Dict[str, str]] = None):
        """Increment a counter metric."""
        key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        self.counters[key] += 1
        self.record_metric(name, self.counters[key], labels)
    
    def set_gauge(self, name: str, value: float, labels: Optional[Dict[str, str]] = None):
        """Set a gauge metric."""
        key = f"{name}:{json.dumps(labels or {}, sort_keys=True)}"
        self.gauges[key] = value
        self.record_metric(name, value, labels)
    
    def start_session(self, session_id: str, agent_name: Optional[str] = None, use_case: Optional[str] = None) -> BuildSession:
        """Start tracking a build session."""
        session = BuildSession(
            session_id=session_id,
            start_time=time.time(),
            agent_name=agent_name,
            use_case=use_case
        )
        self.sessions[session_id] = session
        self.increment_counter("sessions_started")
        logger.info(f"Started session {session_id}")
        return session
    
    def end_session(self, session_id: str, status: str = "completed", error_message: Optional[str] = None):
        """End a build session."""
        if session_id not in self.sessions:
            logger.warning(f"Session {session_id} not found")
            return
        
        session = self.sessions[session_id]
        session.end_time = time.time()
        session.status = status
        session.error_message = error_message
        
        # Record session metrics
        self.record_metric("session_duration", session.duration(), {"status": status})
        self.increment_counter("sessions_completed", {"status": status})
        
        logger.info(f"Ended session {session_id} with status {status}")
    
    def record_session_metric(self, session_id: str, metric_name: str, value: Any):
        """Record a metric for a specific session."""
        if session_id in self.sessions:
            self.sessions[session_id].metrics[metric_name] = value
    
    def get_session_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        total_sessions = len(self.sessions)
        completed_sessions = sum(1 for s in self.sessions.values() if s.status == "completed")
        failed_sessions = sum(1 for s in self.sessions.values() if s.status == "failed")
        
        if completed_sessions > 0:
            avg_duration = sum(s.duration() for s in self.sessions.values() if s.status == "completed") / completed_sessions
        else:
            avg_duration = 0
        
        return {
            "total_sessions": total_sessions,
            "completed_sessions": completed_sessions,
            "failed_sessions": failed_sessions,
            "success_rate": completed_sessions / total_sessions if total_sessions > 0 else 0,
            "average_duration": avg_duration,
            "uptime": time.time() - self.start_time
        }
    
    def get_metric_summary(self, name: str, window_minutes: int = 60) -> Dict[str, float]:
        """Get summary statistics for a metric within a time window."""
        if name not in self.metrics:
            return {}
        
        cutoff_time = time.time() - (window_minutes * 60)
        recent_points = [p for p in self.metrics[name] if p.timestamp >= cutoff_time]
        
        if not recent_points:
            return {}
        
        values = [p.value for p in recent_points]
        return {
            "count": len(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "latest": values[-1] if values else 0
        }
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for external monitoring."""
        return {
            "timestamp": time.time(),
            "session_stats": self.get_session_stats(),
            "counters": dict(self.counters),
            "gauges": dict(self.gauges),
            "metric_summaries": {
                name: self.get_metric_summary(name) 
                for name in self.metrics.keys()
            }
        }


class PerformanceMonitor:
    """Monitor system performance and resource usage."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.monitoring_active = False
    
    async def start_monitoring(self, interval_seconds: int = 30):
        """Start background performance monitoring."""
        self.monitoring_active = True
        logger.info("Started performance monitoring")
        
        while self.monitoring_active:
            try:
                await self._collect_system_metrics()
                await asyncio.sleep(interval_seconds)
            except Exception as e:
                logger.error(f"Error in performance monitoring: {e}")
                await asyncio.sleep(interval_seconds)
    
    def stop_monitoring(self):
        """Stop performance monitoring."""
        self.monitoring_active = False
        logger.info("Stopped performance monitoring")
    
    async def _collect_system_metrics(self):
        """Collect system performance metrics."""
        try:
            import psutil
            
            # CPU usage
            cpu_percent = psutil.cpu_percent(interval=1)
            self.metrics.set_gauge("system_cpu_percent", cpu_percent)
            
            # Memory usage
            memory = psutil.virtual_memory()
            self.metrics.set_gauge("system_memory_percent", memory.percent)
            self.metrics.set_gauge("system_memory_available_mb", memory.available / 1024 / 1024)
            
            # Disk usage
            disk = psutil.disk_usage('/')
            self.metrics.set_gauge("system_disk_percent", (disk.used / disk.total) * 100)
            
            # Process-specific metrics
            process = psutil.Process()
            self.metrics.set_gauge("process_memory_mb", process.memory_info().rss / 1024 / 1024)
            self.metrics.set_gauge("process_cpu_percent", process.cpu_percent())
            
        except ImportError:
            # psutil not available, skip system metrics
            pass
        except Exception as e:
            logger.warning(f"Failed to collect system metrics: {e}")


class HealthChecker:
    """Monitor application health and dependencies."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.health_checks = {}
    
    def register_health_check(self, name: str, check_func):
        """Register a health check function."""
        self.health_checks[name] = check_func
        logger.debug(f"Registered health check: {name}")
    
    async def run_health_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        overall_healthy = True
        
        for name, check_func in self.health_checks.items():
            try:
                start_time = time.time()
                result = await check_func() if asyncio.iscoroutinefunction(check_func) else check_func()
                duration = time.time() - start_time
                
                is_healthy = result.get("healthy", False) if isinstance(result, dict) else bool(result)
                
                results[name] = {
                    "healthy": is_healthy,
                    "duration": duration,
                    "details": result if isinstance(result, dict) else {"status": result}
                }
                
                if not is_healthy:
                    overall_healthy = False
                
                # Record metrics
                self.metrics.record_metric(f"health_check_duration", duration, {"check": name})
                self.metrics.set_gauge(f"health_check_status", 1 if is_healthy else 0, {"check": name})
                
            except Exception as e:
                results[name] = {
                    "healthy": False,
                    "error": str(e),
                    "duration": 0
                }
                overall_healthy = False
                logger.error(f"Health check {name} failed: {e}")
        
        results["overall"] = {"healthy": overall_healthy}
        return results


class AlertManager:
    """Manage alerts and notifications."""
    
    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics = metrics_collector
        self.alert_rules = []
        self.alert_history = deque(maxlen=100)
    
    def add_alert_rule(self, name: str, condition_func, message: str, cooldown_minutes: int = 5):
        """Add an alert rule."""
        self.alert_rules.append({
            "name": name,
            "condition": condition_func,
            "message": message,
            "cooldown": cooldown_minutes * 60,
            "last_triggered": 0
        })
        logger.debug(f"Added alert rule: {name}")
    
    async def check_alerts(self):
        """Check all alert rules and trigger alerts if needed."""
        current_time = time.time()
        
        for rule in self.alert_rules:
            try:
                # Check cooldown
                if current_time - rule["last_triggered"] < rule["cooldown"]:
                    continue
                
                # Evaluate condition
                if rule["condition"](self.metrics):
                    await self._trigger_alert(rule, current_time)
                    
            except Exception as e:
                logger.error(f"Error checking alert rule {rule['name']}: {e}")
    
    async def _trigger_alert(self, rule: Dict[str, Any], timestamp: float):
        """Trigger an alert."""
        alert = {
            "name": rule["name"],
            "message": rule["message"],
            "timestamp": timestamp,
            "severity": "warning"  # Could be configurable
        }
        
        self.alert_history.append(alert)
        rule["last_triggered"] = timestamp
        
        logger.warning(f"ALERT: {rule['name']} - {rule['message']}")
        
        # Here you could add integrations to send alerts via:
        # - Email
        # - Slack
        # - PagerDuty
        # - Discord webhook
        # etc.


# Global metrics collector instance
metrics_collector = MetricsCollector()


# Convenience functions
def record_metric(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Record a metric point."""
    metrics_collector.record_metric(name, value, labels)


def increment_counter(name: str, labels: Optional[Dict[str, str]] = None):
    """Increment a counter."""
    metrics_collector.increment_counter(name, labels)


def set_gauge(name: str, value: float, labels: Optional[Dict[str, str]] = None):
    """Set a gauge value."""
    metrics_collector.set_gauge(name, value, labels)


def start_session(session_id: str, agent_name: Optional[str] = None, use_case: Optional[str] = None) -> BuildSession:
    """Start a build session."""
    return metrics_collector.start_session(session_id, agent_name, use_case)


def end_session(session_id: str, status: str = "completed", error_message: Optional[str] = None):
    """End a build session."""
    metrics_collector.end_session(session_id, status, error_message)
