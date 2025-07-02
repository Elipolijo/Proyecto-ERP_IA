import React, { useState } from 'react';
import { Box, Button } from '@mui/material';
import './SidebarResponsive.css';

const items = [
  { text: 'Dashboard', path: '/dashboard' },
  { text: 'Inventario', path: '/productos' },
  { text: 'Clientes', path: '/clientes' },
];

function SidebarResponsive() {
  const [open, setOpen] = useState(true);

  return (
    <Box
      className={`sidebar-responsive ${open ? 'sidebar-open' : 'sidebar-closed'}`}
      sx={{ height: '100vh', bgcolor: '#fff', borderRight: '1px solid #e5e7eb', transition: 'all 0.3s' }}
    >
      <Box display="flex" justifyContent={open ? 'flex-end' : 'center'} alignItems="center" p={1}>
        <Button onClick={() => setOpen(!open)} variant="outlined" size="small">
          {open ? '<' : '>'}
        </Button>
      </Box>
      <ul style={{ listStyle: 'none', padding: 0 }}>
        {items.map(({ text, path }) => (
          <li key={text} style={{ margin: '16px 0', textAlign: open ? 'left' : 'center' }}>
            <a href={path} style={{ textDecoration: 'none', color: '#374151', fontWeight: 600, fontSize: 16 }}>
              {open ? text : text.charAt(0)}
            </a>
          </li>
        ))}
      </ul>
    </Box>
  );
}

export default SidebarResponsive;
