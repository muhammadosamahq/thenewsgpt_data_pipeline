import React from 'react';

const MetaDataList = ({ metaData }) => {
  return (
    <div className="meta-data-list">
      <h3>Meta Data</h3>
      <ul>
        {metaData.map((item, index) => (
          <li key={index}>{item.property}: {item.value}</li>
        ))}
      </ul>
    </div>
  );
};

export default MetaDataList;
