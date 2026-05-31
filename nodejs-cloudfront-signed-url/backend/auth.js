const { fromTemporaryCredentials } = require("@aws-sdk/credential-providers");

// Create a single, shared credential provider instance
const sharedRoleCredentials = fromTemporaryCredentials({
   params: {
     RoleArn: process.env.AWS_STS_ROLE,
     RoleSessionName: "S3-Presign-App-Session",
   },
   clientConfig: { region: process.env.AWS_REGION }
 }); 

const getCredentialKeys = async () => {
  try {
    console.log("Fetching temporary credentials from STS...");

    const credentials = await sharedRoleCredentials();

    /*
    console.log("Access Key ID:", credentials.accessKeyId);
    console.log("Secret Key:", credentials.secretAccessKey);
    console.log("Session Token:", credentials.sessionToken);
    console.log("Expiration Date:", credentials.expiration);
    */

    return credentials;
  } catch (error) {
    console.error("Failed to fetch credentials:", error);
  }
}

module.exports = {
  sharedRoleCredentials,
  getCredentialKeys
};
