"""
LLM Service Abstraction Layer
Supports multiple language models: Gemma3 (via Replicate) and Gemini (via Google API)
"""

import os
import logging
import asyncio
import requests
import json
from typing import Dict, Any, Optional
from enum import Enum
from dotenv import load_dotenv

import replicate
from .tools_parts_service import tools_parts_extractor, ToolsPartsResponse

logger = logging.getLogger(__name__)
load_dotenv()

# Use direct HTTP requests for Gemini instead of the SDK
GEMINI_AVAILABLE = True

class LLMProvider(Enum):
    GEMMA3 = "gemma3"
    GEMINI = "gemini"
    DEEPSEEK = "deepseek"
    GPT5 = "gpt5"

class LLMService:
    """Unified service for multiple LLM providers."""
    
    def __init__(self):
        self._setup_providers()
    
    def _setup_providers(self):
        """Initialize API clients for all providers."""
        # Replicate for Gemma3, DeepSeek, and GPT-5
        self.replicate_token = os.getenv("REPLICATE_API_TOKEN")
        if self.replicate_token:
            self.replicate_client = replicate.Client(api_token=self.replicate_token)
            self.gemma_model_7b = "google-deepmind/gemma-3-27b-it:c0f0aebe8e578c15a7531e08a62cf01206f5870e9d0a67804b8152822db58c54"
            self.deepseek_model = "deepseek-ai/deepseek-r1"
            self.gpt5_model = "openai/gpt-5"
        else:
            logger.warning("REPLICATE_API_TOKEN not found - Gemma3, DeepSeek, and GPT-5 will not be available")
        
        # Google Gemini using direct HTTP API
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_api_key}"
        
        if self.gemini_api_key and len(self.gemini_api_key.strip()) > 0:
            logger.info("Google Gemini configured successfully with direct HTTP API")
            self.gemini_configured = True
        else:
            logger.warning("GEMINI_API_KEY not found - Gemini will not be available")
            self.gemini_configured = False
    
    def ask_question(
        self, 
        question: str, 
        context: str = "", 
        provider: LLMProvider = LLMProvider.GEMMA3,
        stream: bool = False,
        include_tools_parts: bool = True,
        is_repair_question: bool = False
    ) -> Dict[str, Any]:
        """
        Ask a question using the specified LLM provider.
        
        Args:
            question: The question to ask
            context: Optional context for the question
            provider: Which LLM provider to use
            stream: Whether to stream the response (only supported by some providers)
            
        Returns:
            Dict with 'answer' and 'raw_response' keys
        """
        try:
            # Get the basic response from the LLM
            if provider == LLMProvider.GEMMA3:
                response = self._ask_gemma3(question, context, stream, is_repair_question)
            elif provider == LLMProvider.GEMINI:
                # Check if Gemini is actually available before calling
                if not self.is_provider_available(provider):
                    return {
                        "answer": "WARNING: Gemini is not available. Please check your API key configuration or use Gemma3 instead.",
                        "raw_response": "Provider not available"
                    }
                response = self._ask_gemini(question, context, is_repair_question)
            elif provider == LLMProvider.DEEPSEEK:
                response = self._ask_deepseek(question, context, is_repair_question)
            elif provider == LLMProvider.GPT5:
                response = self._ask_gpt5(question, context, is_repair_question)
            else:
                raise ValueError(f"Unsupported provider: {provider}")
            
            # Extract tools and parts if requested
            if include_tools_parts and "answer" in response:
                tools_parts_data = tools_parts_extractor.extract_tools_and_parts(response["answer"])
                enhanced_response = ToolsPartsResponse(response, tools_parts_data)
                return enhanced_response.to_dict(include_tools_parts=include_tools_parts)
            
            return response
                
        except Exception as e:
            logger.error(f"Error with {provider.value}: {e}")
            # Provide more helpful error messages
            if "Google Generative AI package not available" in str(e):
                error_msg = "WARNING: Gemini service is not available. Please use Gemma3 instead."
            elif "not configured" in str(e):
                error_msg = "WARNING: Gemini API key is not configured. Please use Gemma3 instead."
            else:
                error_msg = f"WARNING: Error with {provider.value} API: {str(e)}"
            
            return {
                "answer": error_msg,
                "raw_response": str(e)
            }
    
    async def ask_question_async(
        self, 
        question: str, 
        context: str = "", 
        provider: LLMProvider = LLMProvider.GEMMA3,
        timeout: int = 120,
        is_repair_question: bool = True  # PDF uploads are typically repair-related
    ) -> Dict[str, Any]:
        """Async wrapper for ask_question with timeout."""
        try:
            return await asyncio.wait_for(
                asyncio.to_thread(self.ask_question, question, context, provider, False, True, is_repair_question),
                timeout=timeout
            )
        except asyncio.TimeoutError:
            logger.error(f"⏳ {provider.value} API request timed out")
            return {"answer": "⚠️ Request timed out.", "raw_response": None}
        except Exception as e:
            logger.exception(f"❌ Unexpected error in {provider.value} async: {e}")
            return {"answer": f"⚠️ Error contacting {provider.value} API.", "raw_response": str(e)}
    
    def _ask_gemma3(self, question: str, context: str = "", stream: bool = False, is_repair_question: bool = False) -> Dict[str, Any]:
        """Ask Gemma-3 via Replicate API."""
        if not hasattr(self, 'replicate_client'):
            raise RuntimeError("Replicate API not configured")
        
        MAX_CONTEXT_CHARS = 2000
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS]
        
        # Build prompt based on whether it's repair-related
        if is_repair_question:
            # Repair-specific prompts with tools/parts requirements
            if context.strip():
                prompt = f"""You are a helpful repair assistant. Based on the following context, please answer the user's question using markdown formatting for better readability.

Context: {context}

Question: {question}

Please provide a well-formatted markdown answer that includes:
- **Bold** for important points
- Numbered lists for step-by-step instructions
- Bullet lists for tools/parts needed
- > Blockquotes for safety warnings

IMPORTANT: At the end of your response, please include a structured section for tools and parts:

### Tools & Parts Required
**Tools:**
- List all tools needed (e.g., screwdriver, multimeter, etc.)

**Parts:**
- List all parts that might need replacement (e.g., battery, screen, etc.)

**Estimated Cost:**
- Provide rough cost estimates if possible

Answer:"""
            else:
                prompt = f"""You are a helpful repair assistant. Please answer the following question using markdown formatting for better readability.

Question: {question}

Please provide a well-formatted markdown answer that includes:
- **Bold** for important points
- Numbered lists for step-by-step instructions
- Bullet lists for tools/parts needed
- > Blockquotes for safety warnings

IMPORTANT: At the end of your response, please include a structured section for tools and parts:

### Tools & Parts Required
**Tools:**
- List all tools needed (e.g., screwdriver, multimeter, etc.)

**Parts:**
- List all parts that might need replacement (e.g., battery, screen, etc.)

**Estimated Cost:**
- Provide rough cost estimates if possible

Answer:"""
        else:
            # General conversation prompts - friendly and natural
            if context.strip():
                prompt = f"""You are a helpful and friendly assistant. Based on the following context, please answer the user's question naturally and conversationally.

Context: {context}

Question: {question}

Please provide a helpful and friendly response. Keep it natural and conversational.

Answer:"""
            else:
                prompt = f"""You are a helpful and friendly assistant. Please answer the following question naturally and conversationally.

Question: {question}

Please provide a helpful and friendly response. Keep it natural and conversational.

Answer:"""
        
        try:
            if stream:
                answer_chunks = []
                for event in replicate.stream(self.gemma_model_7b, input={"prompt": prompt}):
                    if event.event == "output":
                        answer_chunks.append(str(event.data))
                answer_text = "".join(answer_chunks).strip()
                return {"answer": answer_text, "raw_response": answer_chunks}
            
            # Regular call
            output = self.replicate_client.run(self.gemma_model_7b, input={"prompt": prompt})
            answer_text = self._normalize_replicate_output(output)
            
            if answer_text:
                return {"answer": answer_text.strip(), "raw_response": answer_text}
            
            return {"answer": "WARNING: Sorry, I could not get an answer.", "raw_response": ""}
            
        except Exception as e:
            logger.error(f"❌ Gemma3 API failed: {str(e)}")
            raise
    
    def _check_gemini_availability(self) -> bool:
        """Runtime check for Gemini availability."""
        return hasattr(self, 'gemini_configured') and self.gemini_configured
    
    def _ask_gemini(self, question: str, context: str = "", is_repair_question: bool = False) -> Dict[str, Any]:
        """Ask Gemini via Google AI API using direct HTTP requests."""
        # Double-check availability at runtime
        if not self._check_gemini_availability():
            raise RuntimeError("Gemini API not configured")
        
        MAX_CONTEXT_CHARS = 2000
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS]
        
        # Build content based on whether it's repair-related
        if is_repair_question:
            if context.strip():
                # For repair-related questions with PDF context
                prompt_text = f"""You are a helpful repair assistant. Based on the following repair manual context, please answer the user's question clearly and concisely using markdown formatting to make your response well-structured and easy to read.

Context from repair manual:
{context}

User Question: {question}

Please provide a helpful answer formatted in markdown that includes:
- **Direct answer** to the question
- **Relevant repair steps** if applicable (use numbered lists)
- **Safety considerations** if needed (use blockquotes or warning callouts)
- **Tool requirements** if mentioned in the context (use bullet lists)

Use proper markdown formatting including:
- Headers (##, ###) for sections
- **Bold** for important points
- Lists for step-by-step instructions
- > Blockquotes for safety warnings
- `Code blocks` for specific commands or part numbers

IMPORTANT: At the end of your response, please include a structured section for tools and parts:

### Tools & Parts Required
**Tools:**
- List all tools needed (e.g., screwdriver, multimeter, etc.)

**Parts:**
- List all parts that might need replacement (e.g., battery, screen, etc.)

**Estimated Cost:**
- Provide rough cost estimates if possible

Answer:"""
            else:
                # For general repair questions without specific context
                prompt_text = f"""You are a helpful repair assistant. Please answer the following question about device repair, maintenance, or troubleshooting using markdown formatting to make your response well-structured and easy to read.

Question: {question}

Please provide a clear and helpful answer formatted in markdown that includes:
- **Step-by-step guidance** if applicable (use numbered lists)
- **Safety considerations** (use blockquotes or warning callouts)
- **Common tools that might be needed** (use bullet lists)
- **When to consider professional help**

Use proper markdown formatting including:
- Headers (##, ###) for sections
- **Bold** for important points
- Lists for step-by-step instructions
- > Blockquotes for safety warnings
- `Code blocks` for specific commands or part numbers

IMPORTANT: At the end of your response, please include a structured section for tools and parts:

### Tools & Parts Required
**Tools:**
- List all tools needed (e.g., screwdriver, multimeter, etc.)

**Parts:**
- List all parts that might need replacement (e.g., battery, screen, etc.)

**Estimated Cost:**
- Provide rough cost estimates if possible

Answer:"""
        else:
            # General conversation prompts - friendly and natural
            if context.strip():
                prompt_text = f"""You are a helpful and friendly assistant. Based on the following context, please answer the user's question naturally and conversationally.

Context: {context}

Question: {question}

Please provide a helpful and friendly response. Keep it natural and conversational.

Answer:"""
            else:
                prompt_text = f"""You are a helpful and friendly assistant. Please answer the following question naturally and conversationally.

Question: {question}

Please provide a helpful and friendly response. Keep it natural and conversational.

Answer:"""
        
        # Prepare the request payload according to Gemini API format
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt_text
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048,
                "stopSequences": [],
                "candidateCount": 1
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            logger.info(f"Making request to Gemini API: {self.gemini_api_url}")
            
            response = requests.post(
                self.gemini_api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            logger.info(f"Gemini API response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Gemini API error: {response.status_code} - {response.text}")
                raise RuntimeError(f"API request failed with status {response.status_code}: {response.text}")
            
            response_data = response.json()
            logger.info(f"Gemini response data: {json.dumps(response_data, indent=2)}")
            
            # Extract text from Gemini response format
            if "candidates" in response_data and len(response_data["candidates"]) > 0:
                candidate = response_data["candidates"][0]
                logger.info(f"Candidate structure: {json.dumps(candidate, indent=2)}")
                
                # Check for content with parts (normal response)
                if "content" in candidate and "parts" in candidate["content"]:
                    parts = candidate["content"]["parts"]
                    if len(parts) > 0 and "text" in parts[0]:
                        answer_text = parts[0]["text"]
                        return {
                            "answer": answer_text.strip(),
                            "raw_response": response_data
                        }
                
                # Check if content exists but is empty (max tokens exceeded case)
                if "content" in candidate:
                    content = candidate["content"]
                    
                    # Handle case where content is a string
                    if isinstance(content, str):
                        return {
                            "answer": content.strip(),
                            "raw_response": response_data
                        }
                    
                    # Handle case where content has text directly
                    elif "text" in content:
                        return {
                            "answer": content["text"].strip(),
                            "raw_response": response_data
                        }
                    
                    # Handle case where content exists but parts are missing/empty
                    elif "parts" not in content or not content["parts"]:
                        # Check finish reason for more info
                        finish_reason = candidate.get("finishReason", "")
                        if finish_reason == "MAX_TOKENS":
                            return {
                                "answer": "I apologize, but my response was cut off due to length limits. Please try asking a more specific question or break it into smaller parts.",
                                "raw_response": response_data
                            }
                        else:
                            return {
                                "answer": f"I encountered an issue generating a response. Finish reason: {finish_reason}. Please try rephrasing your question.",
                                "raw_response": response_data
                            }
                
                # Try direct text extraction from candidate
                if "text" in candidate:
                    return {
                        "answer": candidate["text"].strip(),
                        "raw_response": response_data
                    }
                
                # Handle case where no content is available at all
                finish_reason = candidate.get("finishReason", "UNKNOWN")
                if finish_reason == "MAX_TOKENS":
                    return {
                        "answer": "I apologize, but my response was cut off due to length limits. Please try asking a more specific question.",
                        "raw_response": response_data
                    }
                else:
                    return {
                        "answer": f"I'm unable to generate a response right now. Please try again or rephrase your question. (Reason: {finish_reason})",
                        "raw_response": response_data
                    }
            
            # If we can't extract text, return a helpful error message
            logger.warning(f"Could not extract text from Gemini response. Full structure: {json.dumps(response_data, indent=2)}")
            return {
                "answer": "I'm sorry, I encountered an issue processing your request. Please try again with a different question or try using a different AI model.",
                "raw_response": response_data
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Gemini API request failed: {str(e)}")
            raise RuntimeError(f"Network error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse Gemini response: {str(e)}")
            raise RuntimeError(f"Invalid JSON response: {str(e)}")
        except Exception as e:
            logger.error(f"Gemini API failed: {str(e)}")
            raise
    
    def _ask_deepseek(self, question: str, context: str = "", is_repair_question: bool = False) -> Dict[str, Any]:
        """Ask DeepSeek-R1 via Replicate API."""
        if not hasattr(self, 'replicate_client'):
            raise RuntimeError("Replicate API not configured")
        
        MAX_CONTEXT_CHARS = 2000
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS]
        
        # Build prompt for DeepSeek with comprehensive formatting instructions
        if context.strip():
            prompt = f"""You are an expert repair assistant with advanced reasoning capabilities. Based on the repair manual context provided, give a comprehensive and well-structured answer to the user's question.

**Repair Manual Context:**
{context}

**User Question:** {question}

**Instructions for your response:**
1. Provide a complete, detailed answer using markdown formatting
2. Structure your response with clear sections using headers (##, ###)
3. Use proper markdown formatting throughout:
   - **Bold** for important tools, parts, and warnings
   - Numbered lists (1., 2., 3.) for step-by-step procedures
   - Bullet lists (-) for tool lists and safety considerations
   - > Blockquotes for critical safety warnings
   - `Code blocks` for specific part numbers or measurements

**Required response structure:**
## Direct Answer
[Directly answer the user's question]

## Tools Required
[List all necessary tools with estimated costs]

## Step-by-Step Process
[If applicable, provide numbered steps]

## Safety Considerations
[Important safety warnings and precautions]

## Cost Analysis
[Breakdown of DIY vs professional costs]

## Additional Tips
[Helpful advice for beginners or troubleshooting]

Please ensure your response is complete and doesn't get cut off. Prioritize the most important information first."""
        else:
            prompt = f"""You are an expert repair assistant with advanced reasoning capabilities. Provide a comprehensive answer to the repair question below.

**User Question:** {question}

**Instructions for your response:**
1. Provide a complete, detailed answer using markdown formatting
2. Structure your response with clear sections using headers (##, ###)
3. Use proper markdown formatting throughout:
   - **Bold** for important tools, parts, and warnings
   - Numbered lists (1., 2., 3.) for step-by-step procedures
   - Bullet lists (-) for tool lists and safety considerations
   - > Blockquotes for critical safety warnings
   - `Code blocks` for specific part numbers or measurements

**Required response structure:**
## Direct Answer
[Directly answer the user's question]

## Tools Required
[List all necessary tools with estimated costs]

## Step-by-Step Process
[If applicable, provide numbered steps]

## Safety Considerations
[Important safety warnings and precautions]

## Cost Analysis
[Breakdown of DIY vs professional costs if applicable]

## Additional Tips
[Helpful advice for beginners or troubleshooting]

Please ensure your response is complete and doesn't get cut off. Prioritize the most important information first."""
        
        try:
            # Try the main DeepSeek model first
            try:
                input_params = {
                    "prompt": prompt,
                    "temperature": 0.3,
                    "max_tokens": 4096,
                    "top_p": 0.8,
                    "repetition_penalty": 1.1
                }
                
                output = self.replicate_client.run(self.deepseek_model, input=input_params)
                answer_text = self._normalize_replicate_output(output)
                
                if answer_text:
                    return {"answer": answer_text.strip(), "raw_response": answer_text}
                    
            except Exception as model_error:
                logger.warning(f"Primary DeepSeek model failed: {model_error}")
                
                # Fallback to alternative DeepSeek model
                try:
                    fallback_model = "deepseek-ai/deepseek-r1-distill-qwen-1.5b"
                    logger.info(f"Trying fallback DeepSeek model: {fallback_model}")
                    
                    output = self.replicate_client.run(fallback_model, input=input_params)
                    answer_text = self._normalize_replicate_output(output)
                    
                    if answer_text:
                        return {"answer": answer_text.strip(), "raw_response": answer_text}
                        
                except Exception as fallback_error:
                    logger.warning(f"Fallback DeepSeek model also failed: {fallback_error}")
                    # Re-raise the original error
                    raise model_error
            
            return {"answer": "WARNING: Sorry, I could not get an answer from DeepSeek.", "raw_response": ""}
            
        except Exception as e:
            logger.error(f"DeepSeek API failed: {str(e)}")
            # Provide helpful error message instead of crashing
            return {
                "answer": f"Sorry, DeepSeek is currently unavailable. Error: {str(e)}. Please try using Gemini or Gemma3 instead.",
                "raw_response": str(e)
            }
    
    def _ask_gpt5(self, question: str, context: str = "", is_repair_question: bool = False) -> Dict[str, Any]:
        """Ask GPT-5 via Replicate API using correct format."""
        if not hasattr(self, 'replicate_client'):
            raise RuntimeError("Replicate API not configured")
        
        MAX_CONTEXT_CHARS = 2000
        if len(context) > MAX_CONTEXT_CHARS:
            context = context[:MAX_CONTEXT_CHARS]
        
        # Build prompt for GPT-5 with comprehensive formatting instructions including proper cost labeling
        if context.strip():
            prompt_text = f"""You are an expert repair assistant. Based on the repair manual context provided, give a comprehensive and well-structured answer to the user's question with proper cost analysis.

**Repair Manual Context:**
{context}

**User Question:** {question}

**Critical Instructions for your response:**
1. Always provide complete answers with proper labels and formatting
2. When discussing costs, ALWAYS include clear labels like "DIY Cost:", "Professional Cost:", "Tool Cost:", etc.
3. Use markdown formatting throughout for better readability
4. Structure your response with clear sections using headers (##, ###)

**Required response structure:**
## Direct Answer
[Directly answer the user's question]

## Cost Breakdown
### DIY Repair Costs:
- **Tools needed:** [List with individual prices, e.g., "Phillips screwdriver: $5-15"]
- **Parts cost:** [Estimated part prices with labels]
- **Total DIY cost:** [Clear total with "Total DIY Cost: $X-Y"]

### Professional Repair Costs:
- **Labor cost:** [Typical labor charges]
- **Parts markup:** [How professionals mark up parts]
- **Total professional cost:** [Clear total with "Total Professional Cost: $X-Y"]

### Cost Comparison:
- **Savings:** [Clear savings calculation with "You could save: $X-Y by doing it yourself"]

## Tools Required
[List all necessary tools with individual estimated costs]

## Step-by-Step Process
[If applicable, provide numbered steps]

## Safety Considerations
[Important safety warnings and precautions]

## Additional Tips
[Helpful advice for beginners]

**IMPORTANT:** Always label your prices clearly (e.g., "DIY Cost: $50-80", "Professional Cost: $150-250", "You save: $100-170"). Never provide bare numbers without context.

Answer:"""
        else:
            prompt_text = f"""You are an expert repair assistant. Provide a comprehensive answer to the repair question with proper cost analysis and clear labeling.

**User Question:** {question}

**Critical Instructions for your response:**
1. Always provide complete answers with proper labels and formatting
2. When discussing costs, ALWAYS include clear labels like "DIY Cost:", "Professional Cost:", "Tool Cost:", etc.
3. Use markdown formatting throughout for better readability
4. Structure your response with clear sections using headers (##, ###)

**Required response structure:**
## Direct Answer
[Directly answer the user's question]

## Cost Breakdown
### DIY Repair Costs:
- **Tools needed:** [List with individual prices, e.g., "Phillips screwdriver: $5-15"]
- **Parts cost:** [Estimated part prices with labels]
- **Total DIY cost:** [Clear total with "Total DIY Cost: $X-Y"]

### Professional Repair Costs:
- **Labor cost:** [Typical labor charges]
- **Parts markup:** [How professionals mark up parts]
- **Total professional cost:** [Clear total with "Total Professional Cost: $X-Y"]

### Cost Comparison:
- **Savings:** [Clear savings calculation with "You could save: $X-Y by doing it yourself"]

## Tools Required
[List all necessary tools with individual estimated costs]

## Step-by-Step Process
[If applicable, provide numbered steps]

## Safety Considerations
[Important safety warnings and precautions]

## Additional Tips
[Helpful advice for beginners]

**IMPORTANT:** Always label your prices clearly (e.g., "DIY Cost: $50-80", "Professional Cost: $150-250", "You save: $100-170"). Never provide bare numbers without context.

Answer:"""
        
        try:
            # GPT-5 via Replicate API - using correct format from docs
            input_params = {
                "prompt": prompt_text,
                "verbosity": "medium",  # Control response length: "low", "medium", "high"
                "reasoning_effort": "medium",  # Control reasoning depth
                "max_completion_tokens": 2048
            }
            
            logger.info(f"Calling GPT-5 with model: {self.gpt5_model}")
            output = self.replicate_client.run(self.gpt5_model, input=input_params)
            answer_text = self._normalize_replicate_output(output)
            
            if answer_text:
                return {"answer": answer_text.strip(), "raw_response": answer_text}
            
            return {"answer": "WARNING: Sorry, I could not get an answer from GPT-5.", "raw_response": ""}
            
        except Exception as e:
            logger.error(f"GPT-5 API failed: {str(e)}")
            raise
    
    def _normalize_replicate_output(self, output) -> str:
        """Normalize Replicate API output into a clean string."""
        if output is None:
            return ""
        if isinstance(output, str):
            return output.strip()
        if isinstance(output, (list, tuple)):
            # Filter out empty strings and join
            filtered_output = [str(x) for x in output if str(x).strip()]
            result = "".join(filtered_output).strip()
            # Ensure we don't have incomplete responses
            if result and not result.endswith(('.', '!', '?', '```', '**', '*')):
                logger.warning(f"Response may be incomplete: ends with '{result[-10:]}'")
            return result
        if isinstance(output, dict):
            return output.get("text", str(output))
        return str(output)
    
    def get_available_providers(self) -> list[LLMProvider]:
        """Get list of available LLM providers based on configuration."""
        available = []
        
        if hasattr(self, 'replicate_client'):
            available.append(LLMProvider.GEMMA3)
            available.append(LLMProvider.DEEPSEEK)
            available.append(LLMProvider.GPT5)
        
        if hasattr(self, 'gemini_configured') and self.gemini_configured:
            available.append(LLMProvider.GEMINI)
        
        return available
    
    def is_provider_available(self, provider: LLMProvider) -> bool:
        """Check if a specific provider is available."""
        return provider in self.get_available_providers()

# Global instance
llm_service = LLMService()

# Backward compatibility functions
def ask_gemma3(question: str, context: str = "", stream: bool = False) -> Dict[str, Any]:
    """Backward compatibility wrapper for Gemma3."""
    return llm_service.ask_question(question, context, LLMProvider.GEMMA3, stream)

async def ask_gemma3_async(question: str, context: str = "", timeout: int = 120) -> Dict[str, Any]:
    """Backward compatibility async wrapper for Gemma3."""
    return await llm_service.ask_question_async(question, context, LLMProvider.GEMMA3, timeout)