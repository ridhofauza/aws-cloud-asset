const express = require("express");
const router = express.Router();
require("dotenv").config();

// S3 Upload File
const { S3Client } = require("@aws-sdk/client-s3");
const { Upload } = require("@aws-sdk/lib-storage");
const { v4: uuidv4 } = require("uuid");
const Busboy = require("busboy");
const { getCredentialKeys } = require("../auth/auth");

const REGION = process.env.AWS_REGION;
const BUCKET_SOURCE = process.env.BUCKET_SOURCE;
const s3 = new S3Client({ 
  region: REGION,
  credentials: getCredentialKeys()
});


// local dependency
const { getVideoList, getVideoByGuid } = require("../services/listVideo");
const { generateLicenseToken } = require("../services/createLicenseToken");
const { fetchAndAppend } = require("../services/storeSqsToJsonFile");

// GET endpoint
router.get("/hello", (req, res) => {
  res.send("Hello world");
});

// get video data from sqs and store to json file
router.get("/sync-video", async (req, res) => {
  try {
    // get video from json file
    await fetchAndAppend();
    res.json({status: 200});
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load videos" });
  }
});

// GET Json List Video
router.get("/videos", async (req, res) => {
  try {
    // get video from json file
    const videos = await getVideoList();
    res.json(videos);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load videos" });
  }
});

// GET video by guid
router.get("/videos/:guid", async (req, res) => {
  try {
    const guid = req.params.guid;
    const video = await getVideoByGuid(guid);
    res.json(video);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load videos" });
  }
});

// GET License Token
router.get("/license-token/:guid", async (req, res) => {
  try {
    const guid = req.params.guid;
    const licenseToken = await generateLicenseToken(guid);
    res.json(licenseToken);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load videos" });
  }
});

// GET License Url
router.get("/license-url/:drmsystem", async (req, res) => {
  try {
    const drmsystem = req.params.drmsystem.toLowerCase();
    let result = "";
    switch (drmsystem) {
      case "widevine":
        result = process.env.WIDEVINE_LICENSE;
        break;
      default:
        break;
    }
    res.json(result);
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to load videos" });
  }
});

// store connections
const clients = {};

router.get("/progress/:id", (req, res) => {
  const id = req.params.id;

  res.setHeader("Content-Type", "text/event-stream");
  res.setHeader("Cache-Control", "no-cache");
  res.setHeader("Connection", "keep-alive");

  clients[id] = res;

  req.on("close", () => {
    delete clients[id];
  });
});

// S3 normal upload, size file <= 5GB and S3 multipart upload, size file > 5GB
router.post("/s3-upload", async (req, res) => {
  try {
    const uploadId = uuidv4();
    const busboy = Busboy({ headers: req.headers });

    busboy.on("file", async (field, file, info) => {
      const { filename } = info;
      const uploader = new Upload({
        client: s3,
        params: {
          Bucket: BUCKET_SOURCE,
          Key: filename,
          Body: file
        },
        queueSize: 4,
        partSize: 5 * 1024 * 1024
      });

      uploader.on("httpUploadProgress", (progress) => {
        const client = clients[uploadId];
        if (client) {
          client.write(`data: ${JSON.stringify(progress)}\n\n`);
        }
      });

      try {
        await uploader.done();

        const client = clients[uploadId];
        if (client) {
          client.write(`data: ${JSON.stringify({ done: true })}\n\n`);
          client.end();
        }

      } catch (err) {
        console.error(err);
      }
    });

    req.pipe(busboy);

    // return upload ID immediately
    res.json({ uploadId });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to generate URL" });
  }
});

// get sqs data
router.post("/get-sqs-output", async (req, res) => {
  try {
    res.json({ status: 200 });
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: "Failed to generate URL" });
  }
});

module.exports = router;