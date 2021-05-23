echo "Updating your system"
apt-get update -y
echo "installing git"
apt-get install git -y
echo "installing rust"
apt-get install rust -y
echo "installing python3"
apt-get install python -y
echo "installing pip"
apt-get install python-pip -y
echo "Updating your Burpdroid (beta-version)"
git clone https://github.com/burpdroid/burpdroid-proxy /data/data/com.termux/files/usr/var/burpdroid-proxy
echo "setting env veriable"
export CRYPTOGRAPHY_DONT_BUILD_RUST=1
echo "installing requirement"
pip install -r /data/data/com.termux/files/usr/var/burpdroid-proxy/requirement.txt
echo "python3 /data/data/com.termux/files/usr/var/burpdroid-proxy/main.py" > /data/data/com.termux/files/usr/bin/burpdroid
chmod +x /data/data/com.termux/files/usr/bin/burpdroid
echo "Burpdroid installed successfully"