const { SQSClient, ReceiveMessageCommand, DeleteMessageBatchCommand } = require("@aws-sdk/client-sqs");
const fs = require("fs");
const path = require("path");
const { getCredentialKeys } = require("../auth/auth");

const sqs = new SQSClient({ 
    region: process.env.AWS_REGION,
    credentials: getCredentialKeys()
});
const QUEUE_URL = process.env.SQS_QUEUE_URL;

async function fetchAndAppend() {
    const filePath = path.join(__dirname, "../data/file_vod.json");
    let allMessages = [];

    while (true) {
        const res = await sqs.send(new ReceiveMessageCommand({
            QueueUrl: QUEUE_URL,
            MaxNumberOfMessages: 10, // max allowed
            WaitTimeSeconds: 10,     // long polling
            VisibilityTimeout: 30
        }));

        if (!res.Messages || res.Messages.length === 0) {
            break; // no more messages
        }

        // Parse messages
        const parsed = res.Messages.map(msg => JSON.parse(msg.Body));

        allMessages.push(...parsed); // spread array

        // Delete messages after processing (important)
        await sqs.send(new DeleteMessageBatchCommand({
            QueueUrl: QUEUE_URL,
            Entries: res.Messages.map(msg => ({
                Id: msg.MessageId,
                ReceiptHandle: msg.ReceiptHandle
            }))
        }));
    }

    // if new data exist
    if (allMessages.length > 0) {
        // Append to JSON file
        let existing = [];

        if (fs.existsSync(filePath)) {
            const file = fs.readFileSync(filePath, "utf-8");
            existing = JSON.parse(file);
        }

        const updated = [...existing, ...allMessages];

        fs.writeFileSync(filePath, JSON.stringify(updated, null, 2));
    }

    console.log(`Saved ${allMessages.length} messages`);
}

module.exports = {
    fetchAndAppend
};