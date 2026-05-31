const { getSignedUrl } = require("@aws-sdk/cloudfront-signer");
const fs = require("fs");

const cloudfrontSignedUrl = (s3ObjectKey) => {
    const cloudfrontDistributionDomain = process.env.CLOUDFRONT_URL;
    const keyPairId = process.env.KEYPAIR_ID;
    const url = `${cloudfrontDistributionDomain}/${s3ObjectKey}`;
    const privateKey = fs.readFileSync(
        process.env.PRIVATE_KEY_PATH,
        "utf8"
    );
    const dateLessThan = new Date(
        Date.now() + 15 * 60 * 1000
    ).toISOString(); // expired after 15 minutes

    return getSignedUrl({
                url,
                keyPairId,
                dateLessThan,
                privateKey,
            });
};

module.exports = {
  cloudfrontSignedUrl
};