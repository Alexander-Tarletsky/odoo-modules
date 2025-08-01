FROM odoo:18.0

USER root

RUN apt-get update && apt-get install -y wget unzip && \
    wget https://github.com/OCA/server-ux/archive/refs/heads/18.0.zip -O /tmp/oca-repo.zip && \
    unzip /tmp/oca-repo.zip -d /tmp && \
    cp -r /tmp/server-ux-18.0/multi_step_wizard /mnt/extra-addons/ && \
    rm -rf /tmp/oca-repo.zip /tmp/server-ux-* && \
    apt-get purge -y wget unzip --auto-remove && \
    rm -rf /var/lib/apt/lists/*

USER odoo

COPY ./openacademy /mnt/extra-addons/openacademy
COPY ./mobilephones /mnt/extra-addons/mobilephones