import React from 'react';

export default function KpiCards({ stats }) {
  const cards = [
    {
      title: 'Total Claims',
      value: stats ? stats.total_claims.toLocaleString() : '...',
      subLabel: 'Ingest Batch',
      subValue: '(100% Vol)',
      icon: 'layers',
      accentColor: '#83CCD2',
      subColor: 'text-primary',
    },
    {
      title: 'Pending Review',
      value: stats ? stats.pending_review.toLocaleString() : '...',
      subLabel: 'Prioritized Queue',
      subValue: '',
      icon: 'hourglass_top',
      accentColor: '#E5B558',
      iconColor: 'text-[#8A6300]',
      subColor: 'text-[#8A6300]',
    },
    {
      title: 'Approved',
      value: stats ? stats.approved.toLocaleString() : '...',
      subLabel: 'Auto-Cleared',
      subValue: '',
      icon: 'check_circle',
      accentColor: '#B2EAD3',
      iconColor: 'text-[#154B35]',
      subColor: 'text-[#154B35]',
    },
    {
      title: 'Doc Review',
      value: stats ? stats.documentation_review.toLocaleString() : '...',
      subLabel: 'Proofs Needed',
      subValue: '',
      icon: 'description',
      accentColor: '#D2CCF2',
      iconColor: 'text-[#464365]',
      subColor: 'text-[#464365]',
    },
    {
      title: 'SIU Escalated',
      value: stats ? stats.siu_escalated.toLocaleString() : '...',
      subLabel: 'Critical Rings',
      subValue: '',
      icon: 'warning',
      accentColor: '#F68BA2',
      iconColor: 'text-tertiary',
      subColor: 'text-tertiary',
      valueColor: 'text-tertiary',
    },
    {
      title: 'LangGraph Runs',
      value: stats ? stats.investigated_count.toLocaleString() : '...',
      subLabel: '6-Agent Audits',
      subValue: '',
      icon: 'account_tree',
      accentColor: '#BEB9E2',
      iconColor: 'text-secondary',
      subColor: 'text-secondary',
    },
  ];

  return (
    <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-space-sm">
      {cards.map((card, idx) => (
        <div
          key={idx}
          className="relative overflow-hidden bg-surface-container-lowest p-space-md rounded-xl shadow-sm flex flex-col justify-between hover:shadow-md transition-shadow border border-outline-variant/15"
        >
          {/* Top pastel accent strip */}
          <div
            className="absolute top-0 left-0 right-0 h-[3px]"
            style={{ backgroundColor: card.accentColor }}
          />

          <div className="flex items-center justify-between text-on-surface-variant mb-1">
            <span className="text-[10px] uppercase font-semibold tracking-wider">
              {card.title}
            </span>
            <span className={`material-symbols-outlined text-[16px] ${card.iconColor || 'text-primary'}`}>
              {card.icon}
            </span>
          </div>

          <div>
            <span className={`text-2xl font-bold tracking-tight ${card.valueColor || 'text-on-surface'}`}>
              {card.value}
            </span>
            <div className="flex items-center gap-1 mt-0.5 text-[10px]">
              <span className={`font-semibold ${card.subColor}`}>{card.subLabel}</span>
              {card.subValue && <span className="text-on-surface-variant">{card.subValue}</span>}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
