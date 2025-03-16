To run, first activate the venv:

./venv/Scripts/activate.ps1

Then run

flask run

flask socketio docs: https://flask-socketio.readthedocs.io/en/latest/getting_started.html#receiving-messages

python socketio docs: https://python-socketio.readthedocs.io/en/stable/intro.html#

source venv/bin/activate

run with gunicorn":
gunicorn --bind 0.0.0.0:8000 app:app

and make sure nginx is wired into this:

server {
    listen 80;
    server_name your_domain_or_ip;

    location / {
        proxy_pass http://127.0.0.1:8000;  # Replace 8000 with Gunicorn's port
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}

under 

/etc/nginx/sites-enabled/default

Now add gunicorn as a service so it starts up

Create sudo nano /etc/systemd/system/gunicorn.service

```
[Unit]
Description=Gunicorn instance to serve app
After=network.target
Requires=nginx.service

[Service]
User=gjh
Group=gjh
ProtectHome=false
WorkingDirectory=/home/gjh/repos/saunaPy
ExecStart=/home/gjh/repos/saunaPy/venv/bin/gunicorn --bind 0.0.0.0:8000 app:app

[Install]
WantedBy=multi-user.target
```

Now install the service: sudo systemctl enable gunicorn.service

