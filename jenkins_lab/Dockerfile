FROM jenkins/jenkins:lts-jdk17

USER root

# Cài đặt các công cụ cần thiết
RUN apt-get update && apt-get install -y lsb-release curl

# Cài đặt Docker CLI (Để Jenkins gọi được lệnh 'docker build')
RUN curl -fsSLo /usr/share/keyrings/docker-archive-keyring.asc \
  https://download.docker.com/linux/debian/gpg
RUN echo "deb [arch=$(dpkg --print-architecture) \
  signed-by=/usr/share/keyrings/docker-archive-keyring.asc] \
  https://download.docker.com/linux/debian \
  $(lsb_release -cs) stable" > /etc/apt/sources.list.d/docker.list
RUN apt-get update && apt-get install -y docker-ce-cli

# Cài đặt Trivy (Để quét lỗ hổng bảo mật image)
RUN curl -sfL https://raw.githubusercontent.com/aquasecurity/trivy/main/contrib/install.sh | sh -s -- -b /usr/local/bin

USER jenkins