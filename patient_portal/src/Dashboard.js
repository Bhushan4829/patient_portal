import React from 'react';
// require('dotenv').config();
function Dashboard() {
    const dashboardUrl = process.env.REACT_APP_DASHBOARD_URL;
    const dashboardName = process.env.REACT_APP_DASHBOARD_NAME;
    return (
        <div style={{ width: '100vw', height: '100vh', overflow: 'hidden' }}>
            <iframe
                title={dashboardName}
                src={dashboardUrl}
                frameBorder="0"
                allowFullScreen={true}
                style={{ width: '100%', height: '100%' }}
            ></iframe>
        </div>
    );
}

export default Dashboard;
