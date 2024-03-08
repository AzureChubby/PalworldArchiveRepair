FROM python:3.10-alpine AS builder

# Set the working directory in the container
WORKDIR /PalRepair

COPY requirements.txt .
COPY repair.py .
COPY start_up.sh .
COPY ArchiveRepair /PalRepair/ArchiveRepair

FROM builder AS runner

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN chmod +x ./start_up.sh

ENTRYPOINT [ "./start_up.sh" ]