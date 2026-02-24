from flask import Flask, render_template_string
import subprocess
import requests
from threading import Thread
import time

app = Flask(__name__)

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <meta name="description" content="">
    <meta name="author" content="">
    <title>AWS EC2 Auto Scaling Lab</title>
    
    <!-- Custom fonts -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet" type="text/css">
    
    <style>
        body {
            margin: 0;
            padding: 0;
            font-family: Arial, sans-serif;
            background-color: #222c3a;
            color: white;
        }
        .welcome-header {
            background-color: #222c3a;
            padding: 20px;
            color: white;
            font-size: 24px;
            font-weight: bold;
        }
        .masthead {
            text-align: center;
            padding: 2rem;
            background-color: #dee1e3;
        }
        .masthead img {
            max-width: 600px;
            width: 100%;
            height: auto;
        }
        .metadata-section {
            padding: 2rem;
            text-align: center;
        }
        .metadata-section h2 {
            margin-bottom: 2rem;
            font-size: 2rem;
        }
        .metadata-item {
            font-size: 1.2rem;
            margin: 1rem 0;
        }
        .aws-orange {
            color: #ff9900;
            font-weight: bold;
        }
        .divider {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem 0;
            background-color: white;
        }
        .divider-line {
            height: 2px;
            width: 200px;
            background-color: #222c3a;
            margin: 0 1rem;
        }
        .divider-star {
            color: #222c3a;
            font-size: 1.5rem;
        }
        .cpu-section {
            text-align: center;
            padding: 2rem;
            background-color: white;
        }
        .cpu-link {
            color: #222c3a;
            text-decoration: underline;
            font-size: 1.2rem;
        }
        .cpu-load {
            font-size: 1.5rem;
            margin: 2rem 0;
            color: #222c3a;
        }
        .refresh-notice {
            margin-top: 1rem;
            font-style: italic;
            color: #a0aec0;
        }
    </style>
</head>

<body>
    <div class="welcome-header">
        WELCOME!
    </div>

    <div class="masthead">
        <img src="https://ws-assets-prod-iad-r-iad-ed304a55c2ca1aee.s3.us-east-1.amazonaws.com/f3a3e2bd-e1d5-49de-b8e6-dac361842e76/powered_by_aws.png" alt="Powered by AWS">
    </div>

    <div class="metadata-section">
        <h2>EC2 Instance Metadata</h2>
        <div class="metadata-item">
            <span class="aws-orange">EC2 Instance ID:</span> {{ instance_id }}
        </div>
        <div class="metadata-item">
            <span class="aws-orange">Availability Zone:</span> {{ availability_zone }}
        </div>
        <div class="metadata-item">
            <span class="aws-orange">Private IP:</span> {{ private_ip }}
        </div>
    </div>

    <div class="divider">
        <div class="divider-line"></div>
        <div class="divider-star">
            <i class="fas fa-star"></i>
        </div>
        <div class="divider-line"></div>
    </div>

    <div class="cpu-section">
        <a href="/generate-load" class="cpu-link">Start CPU Load Generation</a>
        <div class="cpu-load">
            Current CPU Load: <b>{{ cpu_load }}%</b>
        </div>
        {% if is_generating %}
            <div class="refresh-notice">
                Generating CPU Load! (page will refresh in 5 seconds)
                <meta http-equiv="refresh" content="5;url=/" />
            </div>
        {% endif %}
    </div>
</body>
</html>
"""

def get_metadata_token():
    """Get IMDSv2 token for metadata retrieval."""
    try:
        token_response = requests.put(
            "http://169.254.169.254/latest/api/token",
            headers={"X-aws-ec2-metadata-token-ttl-seconds": "21600"},
            timeout=2
        )
        return token_response.text
    except:
        return None

def get_instance_metadata(path):
    """Fetch EC2 instance metadata using IMDSv2."""
    try:
        token = get_metadata_token()
        if token:
            headers = {"X-aws-ec2-metadata-token": token}
        else:
            headers = {}
        
        response = requests.get(
            f"http://169.254.169.254/latest/meta-data/{path}",
            headers=headers,
            timeout=2
        )
        return response.text if response.status_code == 200 else "Not available"
    except:
        return "Not available"

def get_cpu_load():
    """Get current CPU load percentage."""
    try:
        cmd = "vmstat 1 2 | awk '{ for (i=1; i<=NF; i++) if ($i==\"id\") { getline; getline; print $i }}'"
        idle_cpu = float(subprocess.check_output(cmd, shell=True, text=True).strip())
        return round(100 - idle_cpu, 1)
    except:
        return 0

def generate_load():
    """Generate CPU load using dd and gzip commands."""
    cmd = "dd if=/dev/zero bs=100M count=500 | gzip | gzip -d > /dev/null"
    subprocess.Popen(cmd, shell=True)

@app.route('/health')
def health_check():
    """Health check endpoint for ALB."""
    return 'OK', 200

@app.route('/')
def index():
    """Main page route."""
    return render_template_string(
        HTML_TEMPLATE,
        instance_id=get_instance_metadata('instance-id'),
        availability_zone=get_instance_metadata('placement/availability-zone'),
        private_ip=get_instance_metadata('local-ipv4'),
        cpu_load=get_cpu_load(),
        is_generating=False
    )

@app.route('/generate-load')
def trigger_load():
    """Route to trigger CPU load generation."""
    current_load = get_cpu_load()
    is_generating = False
    
    if current_load < 50:
        generate_load()
        is_generating = True
    
    return render_template_string(
        HTML_TEMPLATE,
        instance_id=get_instance_metadata('instance-id'),
        availability_zone=get_instance_metadata('placement/availability-zone'),
        private_ip=get_instance_metadata('local-ipv4'),
        cpu_load=current_load,
        is_generating=is_generating
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)