import { useState } from "react";
import { Box, Button, CircularProgress, TextField, Typography, Alert } from "@mui/material";
import { useNavigate } from "react-router-dom";
import { analyzeChange, AnalyzeChangeResponse } from "../services/api";

interface Props {
  onResult: (result: AnalyzeChangeResponse) => void;
}

export default function ChangeSubmission({ onResult }: Props) {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();

  const handleAnalyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const result = await analyzeChange(text);
      onResult(result);
      navigate("/dependencies");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ maxWidth: 720, mx: "auto", mt: 6, px: 2 }}>
      <Typography variant="h4" fontWeight={700} gutterBottom>
        ChangeGuardian AI
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom>
        Describe your change request and get an instant deployment risk assessment.
      </Typography>
      <TextField
        multiline
        minRows={5}
        fullWidth
        placeholder="e.g. Upgrade payment-service from v4.0 to v4.2"
        value={text}
        onChange={(e) => setText(e.target.value)}
        sx={{ mt: 3 }}
        disabled={loading}
      />
      {error && (
        <Alert severity="error" sx={{ mt: 2 }}>
          {error}
        </Alert>
      )}
      <Button
        variant="contained"
        size="large"
        sx={{ mt: 2 }}
        onClick={handleAnalyze}
        disabled={loading || !text.trim()}
        startIcon={loading ? <CircularProgress size={18} color="inherit" /> : undefined}
      >
        {loading ? "Analyzing…" : "Analyze Change"}
      </Button>
    </Box>
  );
}
