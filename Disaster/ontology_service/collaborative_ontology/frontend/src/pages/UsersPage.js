import React from 'react';
import { Box, Typography } from '@mui/material';

function UsersPage() {
  return (
    <Box>
      <Typography variant="h4" gutterBottom>사용자 관리</Typography>
      <Typography color="textSecondary">사용자 및 권한 관리</Typography>
    </Box>
  );
}

export default UsersPage;
