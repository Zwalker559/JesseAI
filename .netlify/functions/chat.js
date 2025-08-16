const { spawn } = require("child_process")

exports.handler = async function(event) {
  const userMessage = JSON.parse(event.body).message

  return new Promise((resolve) => {
