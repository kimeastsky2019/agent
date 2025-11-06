import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

const resources = {
  ko: {
    translation: {
      navigation: {
        dashboard: '대시보드',
        demand: '수요 분석',
        supply: '공급 분석',
        digital_twin: '디지털 트윈',
        disasters: '재난 관리',
        weather: '날씨',
        ontology: '온톨로지',
        image_broadcasting: '영상 방송',
      },
    },
  },
  en: {
    translation: {
      navigation: {
        dashboard: 'Dashboard',
        demand: 'Demand Analysis',
        supply: 'Supply Analysis',
        digital_twin: 'Digital Twin',
        disasters: 'Disaster Management',
        weather: 'Weather',
        ontology: 'Ontology',
        image_broadcasting: 'Image Broadcasting',
      },
    },
  },
  ja: {
    translation: {
      navigation: {
        dashboard: 'ダッシュボード',
        demand: '需要分析',
        supply: '供給分析',
        digital_twin: 'デジタルツイン',
        disasters: '災害管理',
        weather: '天気',
        ontology: 'オントロジー',
        image_broadcasting: '画像放送',
      },
    },
  },
};

i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    fallbackLng: 'ko',
    debug: false,
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;
