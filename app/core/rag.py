"""
RAG (Retrieval Augmented Generation) Service.

Provides a unified interface for RAG operations used by both the Streamlit UI
and FastAPI service. Implements the ChatReadRetrieveRead pattern from
azure-search-openai-demo.

RAG Flow:
1. User Query → 
2. Azure AI Search (hybrid: vector + semantic) → 
3. Retrieved Documents → 
4. OpenAI (with context) → 
5. Response with citations
"""

import logging
from dataclasses import dataclass, field
from typing import Optional, Generator, Any

from openai import AzureOpenAI
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.search.documents import SearchClient
from azure.search.documents.models import VectorizableTextQuery, QueryType

from .config import Settings, get_settings
from .tracing import (
    get_tracer, 
    add_span_attribute, 
    add_span_event, 
    record_exception
)

logger = logging.getLogger(__name__)


REASONING_MODEL_PREFIXES = (
    'gpt-5',
    'o1',
    'o3',
    'o4',
    'codex-mini',
)


# RAG System Prompt - based on azure-search-openai-demo pattern
RAG_SYSTEM_PROMPT = """You are an intelligent assistant helping users with questions based on the provided documents.
Answer ONLY with the facts listed in the sources below. If there isn't enough information below, say you don't know.
Do not generate answers that don't use the sources below. If asking a clarifying question would help, ask the question.

For tabular information return it as an html table. Do not return markdown format for tables.
Each source has a name followed by colon and the actual information, always include the source name for each fact you use in the response.
Use square brackets to reference the source, for example [source1.pdf]. Don't combine sources, list each source separately, for example [source1.pdf][source2.pdf].

{sources}
"""


@dataclass
class Document:
    """A retrieved document from the search index."""
    content: str
    title: str = ""
    source: str = ""
    page_number: int = 0
    score: float = 0.0
    reranker_score: float = 0.0


@dataclass
class RAGResponse:
    """Response from the RAG service."""
    answer: str
    documents: list[Document] = field(default_factory=list)
    sources_text: str = ""
    system_prompt: str = ""


class RAGService:
    """
    RAG (Retrieval Augmented Generation) Service.
    
    Provides a unified interface for:
    - Document retrieval from Azure AI Search
    - Response generation with Azure OpenAI
    - Source formatting and citation handling
    
    Usage:
        settings = get_settings()
        rag = RAGService(settings)
        
        # For complete response
        response = rag.chat("What is the deductible?")
        print(response.answer)
        
        # For streaming response
        for chunk in rag.chat_stream("What is the deductible?"):
            print(chunk, end="")
    """
    
    def __init__(self, settings: Optional[Settings] = None):
        """
        Initialize the RAG service.
        
        Args:
            settings: Application settings. If None, loads from environment.
        """
        self.settings = settings or get_settings()
        self._openai_client: Optional[AzureOpenAI] = None
        self._search_client: Optional[SearchClient] = None
        self._credential: Optional[DefaultAzureCredential] = None
    
    @property
    def credential(self) -> DefaultAzureCredential:
        """Get or create Azure credential."""
        if self._credential is None:
            self._credential = DefaultAzureCredential()
        return self._credential
    
    @property
    def openai_client(self) -> AzureOpenAI:
        """Get or create Azure OpenAI client."""
        if self._openai_client is None:
            if not self.settings.azure_openai_endpoint:
                raise ValueError("AZURE_OPENAI_ENDPOINT environment variable not set")
            
            token_provider = get_bearer_token_provider(
                self.credential,
                "https://cognitiveservices.azure.com/.default"
            )
            
            self._openai_client = AzureOpenAI(
                azure_endpoint=self.settings.azure_openai_endpoint,
                azure_ad_token_provider=token_provider,
                api_version=self.settings.azure_openai_api_version
            )
        return self._openai_client
    
    @property
    def search_client(self) -> SearchClient:
        """Get or create Azure AI Search client."""
        if self._search_client is None:
            if not self.settings.azure_ai_search_endpoint:
                raise ValueError("AZURE_AI_SEARCH_ENDPOINT environment variable not set")
            
            self._search_client = SearchClient(
                endpoint=self.settings.azure_ai_search_endpoint,
                index_name=self.settings.azure_search_index_name,
                credential=self.credential
            )
        return self._search_client

    @staticmethod
    def _is_reasoning_model(deployment: str) -> bool:
        """Return True when the deployment uses the reasoning-model parameter set."""
        deployment_name = deployment.lower()
        return deployment_name.startswith(REASONING_MODEL_PREFIXES)
    
    def search_documents(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_semantic_ranker: Optional[bool] = None
    ) -> list[Document]:
        """
        Search the Azure AI Search index for relevant documents.
        
        Uses hybrid search (text + vector) with optional semantic ranking.
        
        Args:
            query: User's search query
            top_k: Number of results to return (defaults to settings)
            use_semantic_ranker: Whether to use semantic ranking (defaults to settings)
            
        Returns:
            List of relevant documents with content and metadata
        """
        top_k = top_k or self.settings.search_top_k
        use_semantic_ranker = use_semantic_ranker if use_semantic_ranker is not None else self.settings.use_semantic_ranker
        
        logger.info(f"🔍 RAG STEP 1: Searching for query: '{query}'")
        logger.info(f"   Index: {self.settings.azure_search_index_name}, Top K: {top_k}, Semantic Ranker: {use_semantic_ranker}")
        
        # Start tracing span for document search
        tracer = get_tracer()
        span_context = tracer.start_as_current_span("search_documents") if tracer else None
        
        try:
            if span_context:
                span_context.__enter__()
            
            # Add search parameters as span attributes
            add_span_attribute("search.query", query)
            add_span_attribute("search.top_k", top_k)
            add_span_attribute("search.use_semantic_ranker", use_semantic_ranker)
            add_span_attribute("search.index_name", self.settings.azure_search_index_name)
            add_span_attribute("search.type", "hybrid")
            
            # Use vectorizable text query - the index has an integrated vectorizer
            vector_query = VectorizableTextQuery(
                text=query,
                k_nearest_neighbors=top_k,
                fields=self.settings.vector_field_name,
            )
            
            # Build search parameters based on azure-search-openai-demo pattern
            search_params = {
                "search_text": query,  # Keyword search
                "vector_queries": [vector_query],  # Vector search
                "top": top_k,
                "select": ["content", "title", "source", "page_number"],
            }
            
            # Add semantic ranking if enabled
            if use_semantic_ranker:
                search_params["query_type"] = QueryType.SEMANTIC
                search_params["semantic_configuration_name"] = self.settings.semantic_configuration_name
            
            add_span_event("search_started", {"index": self.settings.azure_search_index_name})
            
            results = self.search_client.search(**search_params)
            
            documents = []
            for result in results:
                documents.append(Document(
                    content=result.get("content", ""),
                    title=result.get("title", ""),
                    source=result.get("source", ""),
                    page_number=result.get("page_number", 0),
                    score=result.get("@search.score", 0),
                    reranker_score=result.get("@search.reranker_score", 0),
                ))
            
            # Add result metrics to span
            add_span_attribute("search.documents_found", len(documents))
            if documents:
                add_span_attribute("search.top_score", documents[0].score)
                sources = [doc.source for doc in documents if doc.source]
                add_span_attribute("search.sources", ", ".join(sources[:5]))
                
                # Add actual document content to trace (truncate if very long)
                for i, doc in enumerate(documents[:5]):  # Limit to first 5 docs
                    content_preview = doc.content[:2000] if len(doc.content) > 2000 else doc.content
                    add_span_attribute(f"search.doc_{i+1}.source", doc.source or "unknown")
                    add_span_attribute(f"search.doc_{i+1}.title", doc.title or "untitled")
                    add_span_attribute(f"search.doc_{i+1}.page", doc.page_number)
                    add_span_attribute(f"search.doc_{i+1}.score", doc.score)
                    add_span_attribute(f"search.doc_{i+1}.content", content_preview)
            
            add_span_event("search_completed", {"documents_found": len(documents)})
            
            logger.info(f"✅ RAG STEP 1 COMPLETE: Retrieved {len(documents)} documents")
            for i, doc in enumerate(documents):
                logger.info(f"   [{i+1}] {doc.source} - Score: {doc.score:.4f}")
            
            return documents
            
        except Exception as e:
            logger.error(f"❌ Search failed: {str(e)}")
            record_exception(e)
            raise
        finally:
            if span_context:
                span_context.__exit__(None, None, None)
    
    def format_sources_for_prompt(self, documents: list[Document]) -> str:
        """
        Format retrieved documents into sources string for the RAG prompt.
        
        Based on azure-search-openai-demo format: "sourcename: content"
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted sources string for injection into system prompt
        """
        logger.info(f"📝 RAG STEP 2: Formatting {len(documents)} documents for prompt")
        
        # Start tracing span for formatting
        tracer = get_tracer()
        span_context = tracer.start_as_current_span("format_sources") if tracer else None
        
        try:
            if span_context:
                span_context.__enter__()
            
            add_span_attribute("format.document_count", len(documents))
            
            if not documents:
                logger.warning("⚠️  No documents to format - sources will be empty")
                add_span_attribute("format.result", "no_sources")
                return "No sources available."
            
            sources = []
            for doc in documents:
                # Create source identifier
                source_name = doc.source or "unknown"
                if doc.page_number:
                    source_name += f"#page={doc.page_number}"
                
                # Format: sourcename: content
                sources.append(f"{source_name}: {doc.content}")
            
            formatted = "\n\n".join(sources)
            
            add_span_attribute("format.output_chars", len(formatted))
            add_span_attribute("format.sources_count", len(sources))
            # Add the actual formatted context (truncate if very long)
            context_for_trace = formatted[:8000] if len(formatted) > 8000 else formatted
            add_span_attribute("format.context_text", context_for_trace)
            
            logger.info(f"✅ RAG STEP 2 COMPLETE: Formatted sources ({len(formatted)} chars)")
            
            return formatted
        finally:
            if span_context:
                span_context.__exit__(None, None, None)
    
    def format_citations_for_display(self, documents: list[Document]) -> str:
        """
        Format retrieved documents for display as citations.
        
        Args:
            documents: List of retrieved documents
            
        Returns:
            Formatted citations string for UI display
        """
        if not documents:
            return "No documents retrieved."
        
        citations = []
        for i, doc in enumerate(documents, 1):
            source_info = f"**{i}. {doc.title or 'Untitled'}**"
            if doc.source:
                source_info += f"\n   📄 {doc.source}"
            if doc.page_number:
                source_info += f" (Page {doc.page_number})"
            if doc.reranker_score:
                source_info += f"\n   🎯 Relevance: {doc.reranker_score:.2f}"
            citations.append(source_info)
        
        return "\n\n".join(citations)
    
    def build_messages(
        self,
        query: str,
        sources: str,
        conversation_history: Optional[list[dict]] = None,
        system_prompt: Optional[str] = None
    ) -> list[dict]:
        """
        Build the messages list for the OpenAI API call.
        
        Args:
            query: Current user query
            sources: Formatted sources string
            conversation_history: Previous messages in conversation
            system_prompt: Custom system prompt (uses default RAG prompt if None)
            
        Returns:
            List of message dicts for the OpenAI API
        """
        # Build system prompt with retrieved sources
        if system_prompt is None:
            system_prompt = RAG_SYSTEM_PROMPT
        
        system_message = system_prompt.format(sources=sources)
        
        logger.info("📋 RAG STEP 3: Building conversation messages")
        
        messages = [{"role": "system", "content": system_message}]
        
        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                messages.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
        
        # Add current user question
        messages.append({"role": "user", "content": query})
        
        return messages
    
    def generate_response(
        self,
        messages: list[dict],
        stream: bool = False,
        max_tokens: Optional[int] = None,
        temperature: Optional[float] = None
    ) -> Any:
        """
        Generate a response from Azure OpenAI.
        
        Args:
            messages: List of message dicts for the API
            stream: Whether to stream the response
            max_tokens: Maximum tokens in response (defaults to settings)
            temperature: Sampling temperature (defaults to settings)
            
        Returns:
            OpenAI response object (streaming or complete)
        """
        deployment = self.settings.azure_openai_chat_deployment
        max_tokens = max_tokens or self.settings.max_tokens
        temperature = temperature if temperature is not None else self.settings.temperature
        is_reasoning_model = self._is_reasoning_model(deployment)
        
        logger.info(f"🤖 RAG STEP 4: Calling OpenAI model: {deployment}")
        logger.info(f"   Message count: {len(messages)}, Stream: {stream}")
        
        # Start tracing span for LLM generation
        tracer = get_tracer()
        span_context = tracer.start_as_current_span("generate_response") if tracer else None
        
        try:
            if span_context:
                span_context.__enter__()
            
            # Add generation parameters as span attributes
            add_span_attribute("gen_ai.system", "azure_openai")
            add_span_attribute("gen_ai.request.model", deployment)
            add_span_attribute("gen_ai.request.max_tokens", max_tokens)
            add_span_attribute("gen_ai.request.temperature", temperature)
            add_span_attribute("gen_ai.request.streaming", stream)
            add_span_attribute("gen_ai.request.message_count", len(messages))
            add_span_attribute("gen_ai.request.reasoning_model", is_reasoning_model)
            
            # Calculate approximate input size
            input_chars = sum(len(m.get("content", "")) for m in messages)
            add_span_attribute("gen_ai.request.input_chars", input_chars)
            
            # Add actual message content to trace
            for i, msg in enumerate(messages):
                role = msg.get("role", "unknown")
                content = msg.get("content", "")
                # Truncate very long messages (system prompt can be large)
                content_preview = content[:10000] if len(content) > 10000 else content
                add_span_attribute(f"gen_ai.request.message_{i}.role", role)
                add_span_attribute(f"gen_ai.request.message_{i}.content", content_preview)
            
            add_span_event("llm_call_started", {"model": deployment, "stream": stream})

            request_args = {
                "model": deployment,
                "messages": messages,
                "stream": stream,
            }
            if is_reasoning_model:
                request_args["max_completion_tokens"] = max_tokens
                add_span_event(
                    "llm_reasoning_compat_mode",
                    {"ignored_parameter": "temperature"}
                )
            else:
                request_args["max_tokens"] = max_tokens
                request_args["temperature"] = temperature

            response = self.openai_client.chat.completions.create(**request_args)
            
            if not stream and hasattr(response, 'usage'):
                add_span_attribute("gen_ai.response.prompt_tokens", response.usage.prompt_tokens)
                add_span_attribute("gen_ai.response.completion_tokens", response.usage.completion_tokens)
                add_span_attribute("gen_ai.response.total_tokens", response.usage.total_tokens)
            
            # Add actual response content for non-streaming
            if not stream and response.choices:
                response_content = response.choices[0].message.content or ""
                add_span_attribute("gen_ai.response.content", response_content)
                add_span_attribute("gen_ai.response.finish_reason", response.choices[0].finish_reason)
            
            add_span_event("llm_call_completed")
            
            return response
            
        except Exception as e:
            record_exception(e)
            raise
        finally:
            if span_context:
                span_context.__exit__(None, None, None)
    
    def chat(
        self,
        query: str,
        conversation_history: Optional[list[dict]] = None,
        top_k: Optional[int] = None,
        use_semantic_ranker: Optional[bool] = None
    ) -> RAGResponse:
        """
        Complete RAG chat flow: retrieve documents and generate response.
        
        This is the main method for non-streaming RAG interactions.
        
        Args:
            query: User's question
            conversation_history: Previous messages for multi-turn
            top_k: Number of documents to retrieve
            use_semantic_ranker: Whether to use semantic ranking
            
        Returns:
            RAGResponse with answer, documents, and metadata
        """
        logger.info("=" * 50)
        logger.info(f"📨 NEW USER QUERY: {query}")
        logger.info("=" * 50)
        
        # Start parent tracing span for the entire RAG workflow
        tracer = get_tracer()
        span_context = tracer.start_as_current_span("rag_chat_workflow") if tracer else None
        
        try:
            if span_context:
                span_context.__enter__()
            
            # Add workflow attributes
            add_span_attribute("rag.query", query)
            add_span_attribute("rag.workflow_type", "complete")
            add_span_attribute("rag.streaming", False)
            add_span_attribute("rag.conversation_turns", len(conversation_history) if conversation_history else 0)
            
            add_span_event("rag_workflow_started", {"query_length": len(query)})
            
            # Step 1: Retrieve documents
            add_span_event("step_1_search_started")
            documents = self.search_documents(query, top_k, use_semantic_ranker)
            add_span_event("step_1_search_completed", {"documents_found": len(documents)})
            
            # Step 2: Format sources
            add_span_event("step_2_format_started")
            sources_text = self.format_sources_for_prompt(documents)
            add_span_event("step_2_format_completed", {"sources_length": len(sources_text)})
            
            # Step 3: Build messages
            add_span_event("step_3_build_messages_started")
            system_prompt = RAG_SYSTEM_PROMPT.format(sources=sources_text)
            messages = self.build_messages(query, sources_text, conversation_history)
            add_span_event("step_3_build_messages_completed", {"message_count": len(messages)})
            
            # Step 4: Generate response
            add_span_event("step_4_generate_started")
            response = self.generate_response(messages, stream=False)
            answer = response.choices[0].message.content
            add_span_event("step_4_generate_completed", {"answer_length": len(answer)})
            
            # Add final workflow metrics
            add_span_attribute("rag.documents_retrieved", len(documents))
            add_span_attribute("rag.answer_length", len(answer))
            add_span_attribute("rag.status", "success")
            
            # Add actual input and output text to workflow span
            add_span_attribute("rag.input.user_query", query)
            add_span_attribute("rag.input.context", sources_text[:8000] if len(sources_text) > 8000 else sources_text)
            add_span_attribute("rag.output.answer", answer)
            
            if hasattr(response, 'usage'):
                add_span_attribute("rag.total_tokens", response.usage.total_tokens)
            
            add_span_event("rag_workflow_completed")
            
            return RAGResponse(
                answer=answer,
                documents=documents,
                sources_text=sources_text,
                system_prompt=system_prompt
            )
            
        except Exception as e:
            add_span_attribute("rag.status", "error")
            record_exception(e)
            raise
        finally:
            if span_context:
                span_context.__exit__(None, None, None)
    
    def chat_stream(
        self,
        query: str,
        conversation_history: Optional[list[dict]] = None,
        top_k: Optional[int] = None,
        use_semantic_ranker: Optional[bool] = None
    ) -> Generator[tuple[str, Optional[RAGResponse]], None, None]:
        """
        Streaming RAG chat flow: retrieve documents and stream response.
        
        Yields chunks of the response as they're generated.
        The final yield includes the complete RAGResponse metadata.
        
        Args:
            query: User's question
            conversation_history: Previous messages for multi-turn
            top_k: Number of documents to retrieve
            use_semantic_ranker: Whether to use semantic ranking
            
        Yields:
            Tuples of (chunk_text, optional_final_response)
            The final_response is only populated on the last yield
        """
        logger.info("=" * 50)
        logger.info(f"📨 NEW USER QUERY (streaming): {query}")
        logger.info("=" * 50)
        
        # Start parent tracing span for the streaming RAG workflow
        tracer = get_tracer()
        span_context = tracer.start_as_current_span("rag_chat_stream_workflow") if tracer else None
        
        try:
            if span_context:
                span_context.__enter__()
            
            # Add workflow attributes
            add_span_attribute("rag.query", query)
            add_span_attribute("rag.workflow_type", "streaming")
            add_span_attribute("rag.streaming", True)
            add_span_attribute("rag.conversation_turns", len(conversation_history) if conversation_history else 0)
            
            add_span_event("rag_stream_workflow_started", {"query_length": len(query)})
            
            # Step 1: Retrieve documents
            add_span_event("step_1_search_started")
            documents = self.search_documents(query, top_k, use_semantic_ranker)
            add_span_event("step_1_search_completed", {"documents_found": len(documents)})
            
            # Step 2: Format sources
            add_span_event("step_2_format_started")
            sources_text = self.format_sources_for_prompt(documents)
            add_span_event("step_2_format_completed", {"sources_length": len(sources_text)})
            
            # Step 3: Build messages
            add_span_event("step_3_build_messages_started")
            system_prompt = RAG_SYSTEM_PROMPT.format(sources=sources_text)
            messages = self.build_messages(query, sources_text, conversation_history)
            add_span_event("step_3_build_messages_completed", {"message_count": len(messages)})
            
            # Step 4: Stream response
            add_span_event("step_4_stream_started")
            response = self.generate_response(messages, stream=True)
            
            full_answer = ""
            chunk_count = 0
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_answer += content
                    chunk_count += 1
                    yield content, None
            
            add_span_event("step_4_stream_completed", {
                "answer_length": len(full_answer),
                "chunk_count": chunk_count
            })
            
            # Add final workflow metrics
            add_span_attribute("rag.documents_retrieved", len(documents))
            add_span_attribute("rag.answer_length", len(full_answer))
            add_span_attribute("rag.stream_chunk_count", chunk_count)
            add_span_attribute("rag.status", "success")
            
            # Add actual input and output text to workflow span
            add_span_attribute("rag.input.user_query", query)
            add_span_attribute("rag.input.context", sources_text[:8000] if len(sources_text) > 8000 else sources_text)
            add_span_attribute("rag.output.answer", full_answer)
            
            add_span_event("rag_stream_workflow_completed")
            
            # Final yield with complete metadata
            final_response = RAGResponse(
                answer=full_answer,
                documents=documents,
                sources_text=sources_text,
                system_prompt=system_prompt
            )
            yield "", final_response
            
        except Exception as e:
            add_span_attribute("rag.status", "error")
            record_exception(e)
            raise
        finally:
            if span_context:
                span_context.__exit__(None, None, None)
    
    def get_documents_for_query(
        self,
        query: str,
        top_k: Optional[int] = None,
        use_semantic_ranker: Optional[bool] = None
    ) -> list[Document]:
        """
        Retrieve documents for a query without generating a response.
        
        Useful for document search functionality without LLM generation.
        
        Args:
            query: Search query
            top_k: Number of documents to retrieve
            use_semantic_ranker: Whether to use semantic ranking
            
        Returns:
            List of retrieved documents
        """
        return self.search_documents(query, top_k, use_semantic_ranker)
