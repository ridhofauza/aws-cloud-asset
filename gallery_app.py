from flask import Flask, render_template_string, request, redirect, url_for
import boto3
from botocore.config import Config
import json
import os
from datetime import datetime, timedelta

app = Flask(__name__)

# Configuration file path
CONFIG_FILE = 'gallery_config.json'

# HTML template including all styling and frontend code
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
    <title>S3 Hands-On Lab</title>
    
    <!-- Custom fonts and styles -->
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Montserrat:400,700" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css?family=Lato:400,700,400italic,700italic" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/@fancyapps/ui@5.0/dist/fancybox/fancybox.css" rel="stylesheet">
    
    <style>
        body {
            font-family: 'Lato', sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f8f9fa;
        }
        .navbar {
            background-color: #252f3f;
            padding: 1.25rem 2rem;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .navbar-brand {
            color: white;
            text-decoration: none;
            font-size: 1.5rem;
            font-weight: bold;
        }
        .navbar-reset {
            color: #ff9900;
            text-decoration: none;
            font-weight: bold;
        }
        .masthead {
            background-color: #dee1e3;
            text-align: center;
            padding: 3rem 0;
        }
        .masthead img {
            max-width: 600px;
            width: 90%;
            height: auto;
            margin: 2rem 0;
        }
        .container {
            max-width: 1140px;
            margin: 0 auto;
            padding: 0 15px;
        }
        .page-section {
            padding: 4rem 0;
            text-align: center;
        }
        .section-heading {
            color: #252f3f;
            font-size: 2rem;
            margin-bottom: 3rem;
            text-transform: uppercase;
        }
        .divider-custom {
            margin: 1.25rem 0 1.5rem;
            width: 100%;
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .divider-custom-line {
            width: 100px;
            height: 0.25rem;
            background-color: #252f3f;
            border-radius: 1rem;
            margin: 0 1rem;
        }
        .divider-custom-icon {
            color: #222c3a;
            font-size: 2rem;
        }
        .form-floating {
            position: relative;
            margin-bottom: 1.5rem;
        }
        .form-control {
            display: block;
            width: 100%;
            padding: 1rem 0.75rem;
            font-size: 1rem;
            line-height: 1.5;
            border: 1px solid #ced4da;
            border-radius: 0.25rem;
            background-color: white;
        }
        .form-floating label {
            position: absolute;
            top: 0;
            left: 0;
            padding: 1rem 0.75rem;
            color: #6c757d;
            transition: all .2s;
            pointer-events: none;
        }
        .form-control:focus + label,
        .form-control:not(:placeholder-shown) + label {
            transform: scale(0.85) translateY(-0.5rem) translateX(0.15rem);
            background-color: white;
            padding: 0 0.5rem;
        }
        .btn-primary {
            display: inline-block;
            font-weight: 600;
            text-align: center;
            padding: 1rem 2rem;
            font-size: 1rem;
            line-height: 1.5;
            border-radius: 0.25rem;
            color: #fff;
            background-color: #222c3a;
            border: none;
            cursor: pointer;
            text-transform: uppercase;
        }
        .btn-primary:hover {
            background-color: #2c3e50;
        }
        .title-band {
            background-color: #252f3f;
            padding: 1.5rem 0;
            width: 100%;
            margin-bottom: 2rem;
        }
        .title-band h1 {
            color: white;
            margin: 0;
            text-align: center;
            font-size: 2rem;
        }
        .gallery {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
            gap: 1rem;
            padding: 1rem;
            place-items: center;  /* Centers items both horizontally and vertically */
        }
        .gallery a {
            display: flex;
            justify-content: center;
            align-items: center;
            width: 100%;
        }
        .gallery img {
            width: 100%;
            height: 200px;
            object-fit: cover;
            border-radius: 4px;
        }
        .text-center {
            text-align: center;
        }
        .reset-link {
            margin-top: 2rem;
            display: block;
            text-align: center;
        }
    </style>
</head>
<body>
    <nav class="navbar">
        <a href="/" class="navbar-brand">WELCOME!</a>
        <a href="/reset" class="navbar-reset">RESET THE S3 LAB FORM</a>
    </nav>

    <header class="masthead">
        <div class="container">
            <img src="https://ws-assets-prod-iad-r-iad-ed304a55c2ca1aee.s3.us-east-1.amazonaws.com/f3a3e2bd-e1d5-49de-b8e6-dac361842e76/powered_by_aws.png" alt="AWS Logo">
        </div>
    </header>

    <div class="title-band">
        <div class="container">
            <h1>S3 Hands-On Lab</h1>
        </div>
    </div>

    <div class="container">
        
        {% if not config %}
        <section class="page-section">
            <h2 class="section-heading">Connect your EC2 Instance to S3</h2>
            
            <div class="divider-custom">
                <div class="divider-custom-line"></div>
                <div class="divider-custom-icon">â˜…</div>
                <div class="divider-custom-line"></div>
            </div>

            <div style="max-width: 600px; margin: 0 auto;">
                <form action="/save-config" method="post">
                    <div class="form-floating">
                        <input type="text" class="form-control" name="bucket" id="bucket" placeholder=" " required>
                        <label for="bucket">Bucket Name</label>
                    </div>
                    <div class="form-floating">
                        <input type="text" class="form-control" name="region" id="region" placeholder=" " required>
                        <label for="region">AWS Region</label>
                    </div>
                    <button type="submit" class="btn-primary">Submit</button>
                </form>
            </div>
        </section>
        {% else %}
        <section class="text-center" style="padding: 3rem 0;">
            <h3>Hosted Images on private S3 Bucket utilizing pre-signed urls</h3>
            <div class="gallery">
                {% for url in presigned_urls %}
                <a href="{{ url }}" data-fancybox="gallery">
                    <img src="{{ url }}" alt="Gallery Image">
                </a>
                {% endfor %}
            </div>
            <a href="/reset" class="reset-link">Reset Configuration</a>
        </section>
        {% endif %}
    </div>

    <script src="https://cdn.jsdelivr.net/npm/@fancyapps/ui@5.0/dist/fancybox/fancybox.umd.js"></script>
    <script>
        Fancybox.bind("[data-fancybox]", {
            // Custom options
        });
    </script>
</body>
</html>
"""

def load_config():
    """Load S3 configuration from JSON file."""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading config: {e}")
    return None

def save_config(bucket, region):
    """Save S3 configuration to JSON file."""
    config = {'bucket': bucket, 'region': region}
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f)
    except Exception as e:
        print(f"Error saving config: {e}")

def get_presigned_urls(bucket, region):
    """Generate presigned URLs for images in the S3 bucket."""
    try:
        # Configure the S3 client with the specific region and signature version
        config = Config(
            region_name=region,
            signature_version='s3v4', # This is important for newer regions
            s3={'addressing_style': 'path'}
        )
        s3_client = boto3.client('s3', config=config)
        
        urls = []
        for i in range(1, 7):
            url = s3_client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': bucket,
                    'Key': f'photo{i}.jpg'
                },
                ExpiresIn=1800
            )
            urls.append(url)
        
        return urls
    except Exception as e:
        print(f"Error generating presigned URLs: {e}")
        return []

@app.route('/')
def index():
    """Main route that displays either the config form or gallery."""
    config = load_config()
    presigned_urls = []
    
    if config:
        presigned_urls = get_presigned_urls(config['bucket'], config['region'])
    
    return render_template_string(
        HTML_TEMPLATE,
        config=config,
        presigned_urls=presigned_urls
    )

@app.route('/save-config', methods=['POST'])
def save_config_route():
    """Route to handle config form submission."""
    bucket = request.form.get('bucket').strip()
    region = request.form.get('region').strip()
    
    if bucket and region:
        save_config(bucket, region)
    
    return redirect(url_for('index'))

@app.route('/reset')
def reset_config():
    """Route to reset the configuration."""
    try:
        if os.path.exists(CONFIG_FILE):
            os.remove(CONFIG_FILE)
    except Exception as e:
        print(f"Error resetting config: {e}")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)
