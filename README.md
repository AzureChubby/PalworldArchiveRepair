# Palworld Archive Repair

## Docker Compose

```yaml
services:
  palworld:
    image: thijsvanloef/palworld-server-docker:latest
    #...
    volumes:
      - ./data:/palworld/
  
  archive-repair:
    image: qian/palworld-archive-repair:latest
    volumes:
      - ./data/Pal/Saved/SaveGames/0/9B6884AE9C8644F0A07D67CA7475E474/Players:/data/Players
      - ./data/log:/var/log
    environment:
      - CRON_REPAIR=*/5 * * * *
    restart: unless-stopped
```