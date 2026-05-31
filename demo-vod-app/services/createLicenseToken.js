const fs = require("fs/promises");
const path = require("path");
const jwt = require("jsonwebtoken");


// get keyId
const getKeyId = async (guid) => {
    const filePath = path.join(__dirname, "../data/file_vod.json");
    const data = await fs.readFile(filePath, "utf-8");

    const jsonData = JSON.parse(data);
    const result = jsonData.find(item => item.guid === guid);
    return result.contentKeySpekeV1.kid;
    /*
    return result.contentKeySpekeV1.kid.map(keyId => ({
        id: keyId
    }));
    */
}

// generate licenseToken
const generateLicenseToken = async (guid) => {
    const listKeyId = await getKeyId(guid);
    const communicationKeyId = process.env.COMM_KEY_ID;
    const communicationKey = Buffer.from(process.env.COMM_KEY, "base64");

    const entitlementMessage = {
        type: "entitlement_message",
        version: 2,
        content_keys_source: {
            inline: [
                {
                    id: listKeyId[0],
                },
            ],
        },
    };

    const licenseServiceMessage = {
        version: 1,
        com_key_id: communicationKeyId,
        message: entitlementMessage,
    };

    // create JWT token
    let jwtAsString = jwt.sign(licenseServiceMessage, communicationKey, {
        "algorithm": "HS256",
        "noTimestamp": true
    });

    return jwtAsString;
}

module.exports = {
    generateLicenseToken
};