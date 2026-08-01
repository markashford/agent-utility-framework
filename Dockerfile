FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser

COPY pyproject.toml README.md ./
COPY __init__.py agent.py ./
COPY tools ./tools
COPY utils ./utils
COPY streamlit_app.py ./streamlit_app.py

RUN pip install --upgrade pip && pip install .[ui]

USER appuser

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
