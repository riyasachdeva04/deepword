// import * as React from 'react';
import { useState } from "react";
import { alpha } from "@mui/material";
import Box from "@mui/material/Box";
import Button from "@mui/material/Button";
import Container from "@mui/material/Container";
// import Link from '@mui/material/Link';
import Stack from "@mui/material/Stack";
import TextField from "@mui/material/TextField";
import Typography from "@mui/material/Typography";
import axios from "axios";
export default function Hero() {
  var [channel, setChannelURL] = useState("");
  var [searchQuery, setSearchQuery] = useState("");
  var [loading, setLoading] = useState(false);
  async function sendURLTODB() {
    setLoading(true);
    console.log(channel);
    const controller = new AbortController();
    const { signal } = controller;

    https://qgrtr737-5001.euw.devtunnels.ms/
    fetch("http://34.121.108.138/", {
      method: "POST",
      // mode: 'no-cors',
      headers: {
        "Content-Type": "application/json",
        // 'Access-Control-Allow-Origin': '*'
      },
      body: JSON.stringify({ search_query: searchQuery, api_url: channel }),
      signal: signal,
    })
      .then((response) => response.json())
      .then((data) => {
        console.log("Success:", data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error:", error);
        setLoading(false);
      });

    // var resp = await axios
    //   .post("http://localhost:5001", {
    //     api_url: channel,
    //     search_query: searchQuery,
    //   })
    //   .catch(() => {
    //     print("err");
    //   });
    console.log(resp);
    setLoading(false);
    alert("Email sent");
  }
  return (
    <Box
      id="hero"
      sx={(theme) => ({
        width: "100%",
        backgroundImage:
          theme.palette.mode === "light"
            ? "linear-gradient(180deg, #CEE5FD, #FFF)"
            : "linear-gradient(#02294F, #090E10)",
        backgroundSize: "100% 20%",
        backgroundRepeat: "no-repeat",
      })}
    >
      <Container
        sx={{
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          pt: { xs: 14, sm: 20 },
          pb: { xs: 8, sm: 12 },
        }}
      >
        <Stack spacing={2} useFlexGap sx={{ width: { xs: "100%", sm: "70%" } }}>
          <Typography
            component="h1"
            variant="h1"
            sx={{
              display: "flex",
              flexDirection: { xs: "column", md: "row" },
              alignSelf: "center",
              textAlign: "center",
            }}
          >
            Welcome to&nbsp;
            <Typography
              component="span"
              variant="h1"
              sx={{
                color: (theme) =>
                  theme.palette.mode === "light"
                    ? "primary.main"
                    : "primary.light",
              }}
            >
              DEEPWORD
            </Typography>
          </Typography>
          <Typography variant="body1" textAlign="center" color="text.secondary">
            Don't let anyone fake you!
          </Typography>
          <Stack
            direction={{ xs: "column", sm: "row" }}
            alignSelf="center"
            spacing={1}
            useFlexGap
            sx={{ pt: 2, width: { xs: "100%", sm: "auto" } }}
          >
            <TextField
              value={channel}
              id="outlined-basic"
              hiddenLabel
              size="small"
              variant="outlined"
              aria-label="Enter your youtube channel link"
              placeholder="Enter your youtube channel link"
              inputProps={{
                autocomplete: "off",
                ariaLabel: "Enter your youtube channel link",
              }}
              onChange={(e) => {
                setChannelURL(e.target.value);
              }}
            />
            <TextField
              value={searchQuery}
              id="outlined-basic"
              hiddenLabel
              size="small"
              variant="outlined"
              aria-label="Enter your search query"
              placeholder="Enter your search query"
              inputProps={{
                autocomplete: "off",
                ariaLabel: "Enter your search query",
              }}
              onChange={(e) => {
                setSearchQuery(e.target.value);
              }}
            />
            {loading ? (
              <Typography>Loading...</Typography>
            ) : (
              <Button variant="contained" color="primary" onClick={sendURLTODB}>
                Start now
              </Button>
            )}
          </Stack>
          {/* <Typography variant="caption" textAlign="center" sx={{ opacity: 0.8 }}>
            By clicking &quot;Start now&quot; you agree to our&nbsp;
            <Link href="#" color="primary">
              Terms & Conditions
            </Link>
            .
          </Typography> */}
        </Stack>
        <Box
          id="image"
          sx={(theme) => ({
            mt: { xs: 8, sm: 10 },
            alignSelf: "center",
            height: { xs: 200, sm: 700 },
            width: "100%",
            backgroundImage:
              theme.palette.mode === "light"
                ? 'url("/static/images/templates/templates-images/hero-light.png")'
                : 'url("/static/images/templates/templates-images/hero-dark.png")',
            backgroundSize: "cover",
            borderRadius: "10px",
            outline: "1px solid",
            outlineColor:
              theme.palette.mode === "light"
                ? alpha("#BFCCD9", 0.5)
                : alpha("#9CCCFC", 0.1),
            boxShadow:
              theme.palette.mode === "light"
                ? `0 0 12px 8px ${alpha("#9CCCFC", 0.2)}`
                : `0 0 24px 12px ${alpha("#033363", 0.2)}`,
          })}
        />
      </Container>
    </Box>
  );
}
