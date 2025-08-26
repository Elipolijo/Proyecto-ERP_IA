import React from 'react';
import { Box, List, ListItem, ListItemText, Typography, Collapse, Divider } from '@mui/material';
import { Link, useLocation } from 'react-router-dom';
import COLORS from '../theme/colors';

const sidebarStructure = [
	{
		section: 'DASHBOARD',
		emoji: '📊',
		items: [{ text: 'Vista general del sistema', path: '/dashboard' }],
	},
	{
		section: 'GESTIÓN DE INVENTARIO',
		emoji: '📦',
		collapsible: true,
		items: [
			{ text: 'Productos', path: '/productos' },
			{ text: 'Categorías', path: '/categorias' },
			{ text: 'Entrada de Stock', path: '/entrada-stock' },
			{ text: 'Movimientos de Stock', path: '/movimiento-stock' },
		],
	},
	{
		section: 'GESTIÓN DE CONTACTOS',
		emoji: '👥',
		collapsible: true,
		items: [
			{ text: 'Clientes', path: '/clientes' },
			{ text: 'Proveedores', path: '/proveedores' },
		],
	},
	{
		section: 'FACTURACIÓN',
		emoji: '💰',
		collapsible: true,
		items: [
			{ text: 'Facturas', path: '/facturas' },
			{ text: 'Reportes de Ventas', path: '/reportes-ventas' },
		],
	},
	{
		section: 'INTELIGENCIA ARTIFICIAL',
		emoji: '🤖',
		collapsible: true,
		items: [
			{ text: 'Predicciones de Demanda', path: '/predicciones-demanda' },
			{ text: 'Análisis de Tendencias', path: '/analisis-tendencias' },
			{ text: 'Alertas Inteligentes', path: '/alertas-inteligentes' },
		],
	},
	{
		section: 'ADMINISTRACIÓN',
		emoji: '👤',
		collapsible: true,
		items: [
			{ text: 'Usuarios', path: '/usuarios' },
			{ text: 'Configuración', path: '/configuracion' },
		],
	},
];

function Sidebar() {
	const location = useLocation();
	const [openSections, setOpenSections] = React.useState({});

	const handleToggle = (section) => {
		setOpenSections((prev) => {
			// Cierra todos los demás y abre solo el actual
			const newState = {};
			newState[section] = !prev[section];
			return newState;
		});
	};

	const handleSidebarMouseLeave = () => {
		setOpenSections({}); // Cierra todos los submenús al salir el mouse
	};

	return (
		<Box
			sx={{
				width: 260,
				bgcolor: COLORS.blanco,
				minHeight: '100vh',
				boxShadow: `2px 0 8px 0 ${COLORS.verdeSuave}`,
				display: 'flex',
				flexDirection: 'column',
				alignItems: 'flex-start',
				p: 0,
			}}
			onMouseLeave={handleSidebarMouseLeave}
		>
			<Box sx={{ width: '100%', p: 3, pb: 1, borderBottom: `1.5px solid ${COLORS.verdeSuave}` }}>
				<Typography variant="h5" fontWeight="bold" color={COLORS.verdeOscuro} letterSpacing={2} fontFamily="monospace">
					POLIX.AI
				</Typography>
				<Typography variant="subtitle2" color={COLORS.verdeBrillante} fontWeight="bold" mt={0.5}>
					Inventory
				</Typography>
			</Box>
			<List sx={{ width: '100%', mt: 2 }}>
				{sidebarStructure.map((section, idx) => (
					<Box key={section.section} sx={{ width: '100%' }}>
						<ListItem
							button={!!section.collapsible}
							onClick={section.collapsible ? () => handleToggle(section.section) : undefined}
							component={section.collapsible ? 'div' : Link}
							to={section.collapsible ? undefined : section.items[0].path}
							sx={{
								color: COLORS.verdeOscuro,
								fontWeight: 'bold',
								fontSize: 14,
								bgcolor: location.pathname.startsWith(section.items[0].path) ? COLORS.verdeSuave : 'transparent',
								borderLeft: location.pathname.startsWith(section.items[0].path) ? `4px solid ${COLORS.verdeBrillante}` : '4px solid transparent',
								pl: 3,
								pt: 1,
								pb: 1,
								'&:hover': {
									bgcolor: COLORS.verdeSuave,
								},
							}}
						>
							<ListItemText primary={`${section.emoji} ${section.section}`} />
						</ListItem>
						{section.collapsible && (
							<Collapse in={!!openSections[section.section]} timeout="auto" unmountOnExit>
								<List component="div" disablePadding>
									{section.items.map((item) => (
										<ListItem
											button
											key={item.text}
											component={Link}
											to={item.path}
											sx={{
												pl: 6,
												color: location.pathname === item.path ? COLORS.verdeBrillante : COLORS.verdeOscuro,
												fontWeight: location.pathname === item.path ? 'bold' : 'normal',
												bgcolor: location.pathname === item.path ? COLORS.verdeSuave : 'transparent',
												'&:hover': {
													bgcolor: COLORS.verdeSuave,
												},
											}}
										>
											<ListItemText primary={item.text} />
										</ListItem>
									))}
								</List>
							</Collapse>
						)}
						{idx < sidebarStructure.length - 1 && <Divider sx={{ my: 1 }} />}
					</Box>
				))}
			</List>
		</Box>
	);
}

export default Sidebar;
