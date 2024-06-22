import React from 'react';

const SummaryList = ({ summaries, onSelectSummary }) => {
  return (
    <div className="summary-list">
      {summaries.map((summary, index) => (
        <div key={index} className="summary-item" onClick={() => onSelectSummary(summary.id)}>
          <h3>{summary.title}</h3>
          <p>{summary.description}</p>
        </div>
      ))}
    </div>
  );
};

export default SummaryList;
