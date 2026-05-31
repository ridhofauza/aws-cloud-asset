const fs = require("fs/promises");
const path = require("path");

const getVideoList = async () => {
  const filePath = path.join(__dirname, "../data/file_vod.json");
  const data = await fs.readFile(filePath, "utf-8");

  const jsonData = JSON.parse(data);
  const result = jsonData.map(item => ({
    guid: item.guid,
    srcVideo: item.srcVideo,
    urlDash: item.egressEndpoints?.DASH,
    thumbnail: item.thumbNailsUrls[0]
  }));
  return result;
};

const getVideoByGuid = async (guid) => {
  const filePath = path.join(__dirname, "../data/file_vod.json");
  const data = await fs.readFile(filePath, "utf-8");

  const jsonData = JSON.parse(data);
  const result = jsonData.map(item => ({
    guid: item.guid,
    srcVideo: item.srcVideo,
    urlDash: item.egressEndpoints?.DASH,
    thumbnail: item.thumbNailsUrls[0]
  }));
  return result.find(item => item.guid === guid);
};

module.exports = {
  getVideoList,
  getVideoByGuid
};