"""
LLM observability configuration for the Text-to-SQL app.
Provides integration with various tracing tools based on environment variables:
- Logfire (https://logfire.pydantic.dev)
- Arize Phoenix (https://phoenix.arize.com)
- Simple stdout logging

This module helps in debugging and monitoring the system's behavior and performance.
"""

import os


def init_tracing():
    """
    Initialize tracing and observability tools based on environment variables.

    Configures integration with the following tools if the corresponding environment
    variables are set.
    """

    if os.getenv("TRACE_LOGFIRE", False):
        print("Initializing Logfire tracing")
        import logfire
        logfire.configure()

    if os.getenv("TRACE_PHOENIX", False):
        print("Initializing Phoenix tracing")
        import phoenix as px
        from phoenix.otel import register
        from openinference.instrumentation.openai import OpenAIInstrumentor
        px.launch_app()
        tracer_provider = register()
        OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

    # if os.getenv("TRACE_SIMPLE", False):
    #     print("Initializing stdout tracing")
    #     set_global_handler("simple")
