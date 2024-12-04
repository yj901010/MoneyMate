export const surveyData = [
    {
      id: 1,
      question: "당신의 연령대는 어떻게 됩니까?",
      type: "single", // 단일 선택
      options: [
        { text: "19세 이하", points: 12.5 },
        { text: "20세 ~ 40세", points: 12.5 },
        { text: "41세 ~ 50세", points: 9.3 },
        { text: "51세 ~ 60세", points: 6.2 },
        { text: "61세 이상", points: 3.1 },
      ],
    },
    {
      id: 2,
      question: "투자하고자 하는 자금의 투자 가능 기간은 얼마나 됩니까?",
      type: "single",
      options: [
        { text: "6개월 이내", points: 3.1 },
        { text: "6개월 이상 ~ 1년 이내", points: 6.2 },
        { text: "1년 이상 ~ 2년 이내", points: 9.3 },
        { text: "2년 이상 ~ 3년 이내", points: 12.5 },
        { text: "3년 이상", points: 15.6 },
      ],
    },
    {
      id: 3,
      question: "다음 중 투자경험과 가장 가까운 것은 어느 것입니까?(중복 가능)",
      type: "multiple", // 다중 선택
      options: [
        { text: "은행의 예·적금, 국채, 지방채, 보증채, MMF, CMA 등", points: 3.1 },
        { text: "금융채, 신용도가 높은 회사채, 채권형펀드, 원금보존추구형 ELS 등", points: 6.2 },
        { text: "신용도 중간 등급의 회사채, 원금의 일부만 보장되는 ELS, 혼합형펀드 등", points: 9.3 },
        { text: "신용도가 낮은 회사채, 주식, 원금이 보장되지 않는 ELS, 시장수익률 수준의 수익을 추구하는 주식형펀드 등", points: 12.5 },
        { text: "ELW, 선물옵션, 시장수익률 이상의 수익을 추구하는 주식형펀드, 파생상품에 투자하는 펀드, 주식 신용거래 등", points: 15.6 },
      ],
    },
    {
      id: 4,
      question: "금융상품 투자에 대한 본인의 지식수준은 어느 정도라고 생각하십니까?",
      type: "single",
      options: [
        { text: "매우 낮은 수준", points: 3.1 },
        { text: "낮은 수준", points: 6.2 },
        { text: "높은 수준", points: 9.3 },
        { text: "매우 높은 수준", points: 12.5 },
      ],
    },
    {
      id: 5,
      question: "현재 투자하고자 하는 자금은 전체 금융자산(부동산 등을 제외) 중 어느 정도의 비중을 차지합니까?",
      type: "single",
      options: [
        { text: "10% 이내", points: 15.6 },
        { text: "10% 이상 ~ 20% 이내", points: 12.5 },
        { text: "20% 이상 ~ 30% 이내", points: 9.3 },
        { text: "30% 이상 ~ 40% 이내", points: 6.2 },
        { text: "40% 이상", points: 3.1 },
      ],
    },
    {
      id: 6,
      question: "다음 중 당신의 수입원을 가장 잘 나타내고 있는 것은 어느 것입니까?",
      type: "single",
      options: [
        { text: "현재 일정한 수입이 발생하고 있으며, 향후 현재 수준을 유지하거나 증가할 것으로 예상된다.", points: 9.3 },
        { text: "현재 일정한 수입이 발생하고 있으나, 향후 감소하거나 불안정할 것으로 예상된다.", points: 6.2 },
        { text: "현재 일정한 수입이 없으며, 연금이 주수입원이다.", points: 3.1 },
      ],
    },
    {
      id: 7,
      question: "만약 투자원금에 손실이 발생할 경우 다음 중 감수할 수 있는 손실 수준은 어느 것입니까?",
      type: "single",
      options: [
        { text: "무슨 일이 있어도 투자원금은 보전되어야 한다.", points: 6.2 },
        { text: "10% 미만까지는 손실을 감수할 수 있을 것 같다.", points: 6.2 },
        { text: "20% 미만까지는 손실을 감수할 수 있을 것 같다.", points: 12.5 },
        { text: "기대수익이 높다면 위험이 높아도 상관하지 않겠다.", points: 18.7 },
      ],
    },
  ];
  

export default surveyData;