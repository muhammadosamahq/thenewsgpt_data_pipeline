import React from 'react';

const StatsTable = ({ stats }) => {
  return (
    <div className="stats-table">
      <h3>Stats</h3>
      <table>
        <thead>
          <tr>
            <th>Property</th>
            <th>Value</th>
          </tr>
        </thead>
        <tbody>
          {stats.map((stat, index) => (
            <tr key={index}>
              <td>{stat.property}</td>
              <td>{stat.value}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default StatsTable;
