# arxiv_alert

## 1. build env
```shell
conda create -n arxiv python=3.8
conda activate arxiv
conda install PyYaml
conda install feedparser==5.2.1
```
## 2. Run
```shell
python arxiv_mail_alert.py --config_path config-keyword.yaml
```
# Daily alert

You need to edit your crontab to add an entry for your script. You can do this by running:

```shell
crontab -e
```
Then, add the following line to your crontab to run your script at 9 AM every weekday (Monday to Friday):
```shell
0 9 * * 1-5 cd ~/workshop/code/auto_mail_alert/ && source /opt/miniconda3/bin/activate arxiv && python arxiv_alert.py --config_path config-keyword.yaml
```
To make sure the script is running as expected, you can redirect the output and errors to a log file. Modify your crontab entry as follows:

```shell
0 9 * * 1-5 cd ~/workshop/code/auto_mail_alert/ && source /opt/miniconda3/bin/activate arxiv && python arxiv_alert.py --config_path config-keyword.yaml >> ~/workshop/code/auto_mail_alert/arxiv_mail.log 2>&1
```
You can verify that your cron job is set up correctly by running:
```shell
crontab -l
```
it will output as follows contents in your screen:
```shell
0 9 * * 1-5 cd ~/workshop/code/auto_mail_alert/ && source /opt/miniconda3/bin/activate arxiv && python arxiv_alert.py --config_path config-keyword.yaml >> ~/workshop/code/auto_mail_alert/arxiv_mail.log 2>&1
```
