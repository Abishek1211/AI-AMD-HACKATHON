import { Box, Chip, Paper, Typography, Divider, List, ListItem, ListItemText } from "@mui/material";
import { AnalyzeChangeResponse } from "../services/api";

const strategyDescription: Record<string, string> = {
  direct: "Deploy directly to all instances at once. Suitable for low-risk, well-tested changes.",
  canary: "Roll out to a small percentage of traffic first, monitor, then expand gradually.",
  "blue-green": "Maintain two identical environments and switch traffic instantly after validation.",
  "feature-flag": "Deploy behind a flag and enable incrementally per user segment.",
  "staged-rollout": "Progressively roll out across regions or clusters with automated health checks.",
};

interface Props {
  result: AnalyzeChangeResponse | null;
}

export default function Recommendation({ result }: Props) {
  if (!result) {
    return (
      <Box sx={{ mt: 4, textAlign: "center" }}>
        <Typography color="text.secondary">No analysis result yet. Submit a change first.</Typography>
      </Box>
    );
  }

  const { recommendation, explanation, incidents } = result;
  const desc = strategyDescription[recommendation] ?? "";

  return (
    <Box sx={{ maxWidth: 900, mx: "auto", mt: 4, px: 2 }}>
      <Typography variant="h5" fontWeight={700} gutterBottom>
        Deployment Recommendation
      </Typography>

      <Paper sx={{ p: 3, mb: 3 }} variant="outlined">
        <Typography variant="subtitle2" gutterBottom>
          Recommended Strategy
        </Typography>
        <Chip label={recommendation.toUpperCase()} color="primary" sx={{ fontWeight: 700, fontSize: 14, mb: 1 }} />
        <Typography variant="body2" color="text.secondary">
          {desc}
        </Typography>
      </Paper>

      <Paper sx={{ p: 3, mb: 3 }} variant="outlined">
        <Typography variant="subtitle2" gutterBottom>
          Explanation
        </Typography>
        <Typography variant="body2" color="text.secondary">
          {explanation}
        </Typography>
      </Paper>

      {incidents.length > 0 && (
        <Paper sx={{ p: 3 }} variant="outlined">
          <Typography variant="subtitle2" gutterBottom>
            Historical Evidence
          </Typography>
          <List dense>
            {incidents.map((inc, i) => (
              <Box key={inc.id ?? i}>
                <ListItem alignItems="flex-start">
                  <ListItemText
                    primary={
                      <>
                        <Chip
                          label={inc.severity}
                          size="small"
                          color={inc.severity === "CRITICAL" ? "error" : "warning"}
                          sx={{ mr: 1 }}
                        />
                        {inc.title}
                      </>
                    }
                    secondary={`Root cause: ${inc.root_cause}`}
                  />
                </ListItem>
                {i < incidents.length - 1 && <Divider component="li" />}
              </Box>
            ))}
          </List>
        </Paper>
      )}
    </Box>
  );
}
