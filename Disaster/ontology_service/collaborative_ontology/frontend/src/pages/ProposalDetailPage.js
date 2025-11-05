import React from 'react';
import { Box, Typography } from '@mui/material';
import { useParams } from 'react-router-dom';

function ProposalDetailPage() {
  const { id } = useParams();
  return (
    <Box>
      <Typography variant="h4">제안 상세 #{id}</Typography>
    </Box>
  );
}

export default ProposalDetailPage;
