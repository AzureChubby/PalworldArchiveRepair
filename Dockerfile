FROM python:3.10-alpine AS builder

# Set the working directory in the container
WORKDIR /PalRepair

COPY requirements.txt .
COPY repair.py .
COPY ArchiveRepair /PalRepair/ArchiveRepair

FROM builder AS runner

VOLUME /data

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

#CMD ["chmod", "+x ~/PalRepair/repair.py"]
ARG CRON_REPAIR="*/1 * * * *"
ENV CRON_REPAIR $CRON_REPAIR
RUN echo "$CRON_REPAIR python /PalRepair/repair.py >> /var/log/repair.log 2>&1" > /etc/crontabs/root

# # Run script.py when the container launches
CMD ["python", "repair.py >> /var/log/repair.log 2>&1"]
#ENTRYPOINT [ "python", "./repair.py" ]

# 启动 cron service
CMD ["crond", "-f"]

