FROM public.ecr.aws/lambda/python:3.11

RUN pip install --upgrade pip setuptools wheel

COPY ml_layer-requirements.txt /tmp/ml_layer-requirements.txt

# Install dependencies into /opt (where layers are mounted)
RUN pip install --no-cache-dir \
    --only-binary=:all: \
    -r /tmp/ml_layer-requirements.txt \
    -t /opt/python
