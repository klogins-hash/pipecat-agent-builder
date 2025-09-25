"""Documentation vectorization system for Pipecat knowledge base."""

import os
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
import asyncio
import aiofiles
from dataclasses import dataclass

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document

from core.config import settings
from core.logger import setup_logger

logger = setup_logger("vectorizer")


@dataclass
class DocumentChunk:
    """Represents a chunk of documentation."""
    content: str
    metadata: Dict[str, Any]
    chunk_id: str
    source_file: str
    section: str
    subsection: Optional[str] = None


class PipecatDocumentationVectorizer:
    """Vectorizes Pipecat documentation for efficient retrieval."""
    
    def __init__(self):
        self.embedding_model = SentenceTransformer(settings.embedding_model)
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            separators=["\n\n", "\n", ".", "!", "?", ",", " ", ""]
        )
        
        # Initialize ChromaDB
        self.chroma_client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False)
        )
        
        # Create or get collection
        self.collection = self.chroma_client.get_or_create_collection(
            name="pipecat_docs",
            metadata={"description": "Pipecat documentation knowledge base"}
        )
    
    async def vectorize_documentation(self, docs_path: Optional[str] = None) -> None:
        """Vectorize all documentation files."""
        docs_path = docs_path or settings.docs_path
        logger.info(f"Starting vectorization of documentation at: {docs_path}")
        
        # Find all .mdx and .md files
        doc_files = []
        for ext in ["*.mdx", "*.md"]:
            doc_files.extend(Path(docs_path).rglob(ext))
        
        logger.info(f"Found {len(doc_files)} documentation files")
        
        all_chunks = []
        for file_path in doc_files:
            try:
                chunks = await self._process_file(file_path)
                all_chunks.extend(chunks)
                logger.debug(f"Processed {file_path.name}: {len(chunks)} chunks")
            except Exception as e:
                logger.error(f"Error processing {file_path}: {e}")
        
        # Store in vector database
        await self._store_chunks(all_chunks)
        logger.info(f"Vectorization complete. Stored {len(all_chunks)} chunks")
    
    async def _process_file(self, file_path: Path) -> List[DocumentChunk]:
        """Process a single documentation file."""
        async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
            content = await f.read()
        
        # Extract metadata from frontmatter
        metadata = self._extract_frontmatter(content)
        
        # Remove frontmatter from content
        content = self._remove_frontmatter(content)
        
        # Determine section from file path
        relative_path = file_path.relative_to(settings.docs_path)
        section = self._determine_section(relative_path)
        
        # Extract code blocks for special handling
        code_blocks = self._extract_code_blocks(content)
        
        # Split content into chunks
        documents = [Document(page_content=content, metadata=metadata)]
        text_chunks = self.text_splitter.split_documents(documents)
        
        chunks = []
        for i, chunk in enumerate(text_chunks):
            # Use full relative path to ensure unique IDs
            safe_path = str(relative_path).replace("/", "_").replace(".", "_")
            chunk_id = f"{safe_path}_chunk_{i}"
            
            # Enhanced metadata
            chunk_metadata = {
                **metadata,
                "source_file": str(relative_path),
                "section": section,
                "chunk_index": i,
                "file_type": file_path.suffix,
                "has_code": len(self._extract_code_blocks(chunk.page_content)) > 0
            }
            
            chunks.append(DocumentChunk(
                content=chunk.page_content,
                metadata=chunk_metadata,
                chunk_id=chunk_id,
                source_file=str(relative_path),
                section=section
            ))
        
        # Add code blocks as separate chunks
        for j, code_block in enumerate(code_blocks):
            safe_path = str(relative_path).replace("/", "_").replace(".", "_")
            chunk_id = f"{safe_path}_code_{j}"
            code_metadata = {
                **metadata,
                "source_file": str(relative_path),
                "section": section,
                "chunk_type": "code",
                "language": code_block.get("language", "unknown"),
                "is_example": True
            }
            
            chunks.append(DocumentChunk(
                content=code_block["content"],
                metadata=code_metadata,
                chunk_id=chunk_id,
                source_file=str(relative_path),
                section=section
            ))
        
        return chunks
    
    def _extract_frontmatter(self, content: str) -> Dict[str, Any]:
        """Extract YAML frontmatter from markdown."""
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        
        if not match:
            return {}
        
        try:
            import yaml
            return yaml.safe_load(match.group(1)) or {}
        except ImportError:
            logger.warning("PyYAML not installed, skipping frontmatter parsing")
            return {}
        except Exception as e:
            logger.warning(f"Error parsing frontmatter: {e}")
            return {}
    
    def _remove_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from content."""
        frontmatter_pattern = r'^---\s*\n.*?\n---\s*\n'
        return re.sub(frontmatter_pattern, '', content, flags=re.DOTALL)
    
    def _determine_section(self, relative_path: Path) -> str:
        """Determine documentation section from file path."""
        parts = relative_path.parts
        if len(parts) > 0:
            return parts[0]
        return "root"
    
    def _extract_code_blocks(self, content: str) -> List[Dict[str, str]]:
        """Extract code blocks from markdown content."""
        code_pattern = r'```(\w+)?\s*\n(.*?)\n```'
        matches = re.findall(code_pattern, content, re.DOTALL)
        
        code_blocks = []
        for language, code in matches:
            if code.strip():  # Only include non-empty code blocks
                code_blocks.append({
                    "language": language or "text",
                    "content": code.strip()
                })
        
        return code_blocks
    
    async def _store_chunks(self, chunks: List[DocumentChunk]) -> None:
        """Store chunks in vector database."""
        if not chunks:
            return
        
        # Prepare data for ChromaDB
        documents = [chunk.content for chunk in chunks]
        metadatas = [chunk.metadata for chunk in chunks]
        ids = [chunk.chunk_id for chunk in chunks]
        
        # Generate embeddings
        logger.info("Generating embeddings...")
        embeddings = self.embedding_model.encode(documents, show_progress_bar=True)
        
        # Store in ChromaDB
        logger.info("Storing in vector database...")
        self.collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings.tolist()
        )
    
    async def search(self, query: str, n_results: int = 5, section_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search the vectorized documentation."""
        where_clause = {}
        if section_filter:
            where_clause["section"] = section_filter
        
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause if where_clause else None
        )
        
        # Format results
        formatted_results = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else None,
                    "id": results["ids"][0][i] if results["ids"] else None
                })
        
        return formatted_results
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the vectorized documentation."""
        count = self.collection.count()
        return {
            "total_chunks": count,
            "collection_name": self.collection.name,
            "embedding_model": settings.embedding_model
        }


# Convenience function for external use
async def vectorize_pipecat_docs(docs_path: Optional[str] = None) -> PipecatDocumentationVectorizer:
    """Vectorize Pipecat documentation and return vectorizer instance."""
    vectorizer = PipecatDocumentationVectorizer()
    await vectorizer.vectorize_documentation(docs_path)
    return vectorizer
