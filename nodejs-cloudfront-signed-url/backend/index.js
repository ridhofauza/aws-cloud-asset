const express = require("express");
const cors = require("cors");
require("dotenv").config();

const app = express();
app.use(cors());

const { 
    PutObjectCommand, 
    S3Client,
    GetObjectCommand
 } = require("@aws-sdk/client-s3");
const {
  getSignedUrl,
  S3RequestPresigner,
} = require("@aws-sdk/s3-request-presigner");

const { getCredentialKeys } = require("./auth");
const { cloudfrontSignedUrl } = require("./cloudfront-service");

const s3 = new S3Client({ 
  region: process.env.AWS_REGION,
  credentials: getCredentialKeys()
});


app.get("/presigned-url", async (req, res) => {
  try {
    const key = req.query.key;

    if (!key) {
      return res.status(400).json({
        message: "Missing object key",
      });
    }

    const command = new GetObjectCommand({
      Bucket: process.env.S3_BUCKET_NAME,
      Key: key,
    });

    const signedUrl = await getSignedUrl(
      s3,
      command,
      {
        expiresIn: 60 * 5, // 5 minutes
      }
    );

    res.json({
      url: signedUrl,
    });

  } catch (error) {
    console.error(error);

    res.status(500).json({
      message: "Failed to generate presigned URL",
    });
  }
});

app.get("/cloudfront-signed-url", async (req, res) => {
  try {
    const key = req.query.key;

    if (!key) {
      return res.status(400).json({
        message: "Missing object key",
      });
    }

    res.json({
      url: cloudfrontSignedUrl(key),
    });

  } catch (error) {
    console.error(error);

    res.status(500).json({
      message: "Failed to generate presigned URL",
    });
  }
});


app.listen(process.env.PORT, () => {
  console.log(
    `Server running on port ${process.env.PORT}`
  );
});

