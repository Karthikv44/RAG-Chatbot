"""
OpenTelemetry setup.
Exports to console locally. Swap ConsoleSpanExporter for
OTLPSpanExporter (Datadog/AWS X-Ray) in production.
"""
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


def setup_tracing(app, engine) -> None:
    resource = Resource.create({"service.name": "rag-chatbot"})
    provider = TracerProvider(resource=resource)

    # Local: console exporter — swap for OTLP/Datadog in prod
    exporter = ConsoleSpanExporter()
    provider.add_span_processor(BatchSpanProcessor(exporter))
    trace.set_tracer_provider(provider)

    FastAPIInstrumentor.instrument_app(app)
    SQLAlchemyInstrumentor().instrument(engine=engine)


def get_tracer(name: str = "rag-chatbot") -> trace.Tracer:
    return trace.get_tracer(name)
