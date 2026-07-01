"""
This file handles connecting to Ollama, sending a prompt, receiving a 
response, and handling errors
"""

import time
from langchain_ollama import OllamaLLM

from src.shared.utils.logging import get_logger
from src.backend.core.settings import get_yaml_config

logger = get_logger("llm")

_llm = None


def _get_llm_config() -> dict:
    config = get_yaml_config()
    return config["llm"]


def _get_llm() -> OllamaLLM:
    # Creating or returning cached Ollama LLM instance

    global _llm
    if _llm is not None:
        return _llm

    llm_config = _get_llm_config()

    logger.info(f"Initializing LLM ... ")
    logger.info(
        f"model : {llm_config['model']} | "
        f"host : {llm_config['host']}"
    )

    _llm = OllamaLLM(
        model=llm_config["model"],
        base_url=llm_config["url"],
        temperature=llm_config.get("temperature", 0.2),
        timeout=llm_config.get("timeout", 120),
    )

    logger.info("LLM client initialized")
    return _llm


def invoke(prompt: str) -> str:
    # Sends a prompt to the local LLM and return the response

    llm_config = _get_llm_config()
    max_retries = llm_config.get("max_retries", 2)
    llm = _get_llm()

    for attempt in range(max_retries):
        try:
            logger.info(
                f"LLM invoke attempt {attempt + 1}/{max_retries} | "
                f"prompt_length : {len(prompt)}"
            )

            start_time = time.time()
            response = llm.invoke(prompt)
            elapsed = time.time() - start_time

            if not response or not response.strip():
                logger.warning(
                    f"LLM returned empty response on attempt {attempt + 1}"
                )
                continue

            logger.info(
                f"LLM response received | "
                f"response_length : {len(response)} | "
                f"time taken : {elapsed:.1f}s"
            )
            return response.strip()

        except Exception as e:
            logger.error(
                f"LLM invoke failed on attempt {attempt + 1}: {e}"
            )

            if attempt + 1 < max_retries:
                logger.info("Retrying ...")
                continue

    logger.error("All LLM invoke attempts failed")
    return ""