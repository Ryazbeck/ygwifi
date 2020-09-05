sudo cp ygwifi/docker.ygwifi.service /etc/systemd/system/
sudo systemctl enable docker.ygwifi
sudo systemctl start docker.ygwifi
rm -rf ygwifi