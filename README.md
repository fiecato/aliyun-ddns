# Dynamic domain name resolution

## install

[python aliyun ddns sdk install](https://help.aliyun.com/document_detail/29821.html?spm=a2c4g.11186623.2.39.390d6379r8f9SE)

Because the script is python3, you need to execute `pip3 install -r requirements.txt` to install the dependent packages

## config

First, modify `domain.cfg.tmp` to `domain.cfg`.

Then, replace the content inside with yours

Because I only used Aliyun's ddns dynamic analysis, so the keyid and scerect in the access are under your Aliyun account.

**Regional node** The available regions depend on your Alibaba Cloud account level. There are only four ordinary users, namely Hangzhou, Shanghai, Shenzhen, and Hebei. Please refer to the official website API for details.
