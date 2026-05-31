const express = require("express");
const cors = require("cors");

const app = express();
app.use(cors());
app.use(express.json());

const videoRoutes = require("./routes/videoRoutes");

app.use("/api", videoRoutes);

app.listen(3000, () => console.log("Server running on port 3000"));