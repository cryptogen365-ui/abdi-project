import React, {useMemo, useState} from 'react';
import {createRoot} from 'react-dom/client';
import {Activity, AlertTriangle, ArrowLeft, Bell, ChevronDown, CircleUserRound, ClipboardCheck, Compass, FileBarChart, Gauge, Goal, LayoutDashboard, Menu, Network, Plus, Search, Settings, ShieldCheck, Sparkles, Target, TrendingUp, Users, Workflow, X, Zap} from 'lucide-react';
import {Area, AreaChart, Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis} from 'recharts';
import './styles.css';

const nav = [
  ['داشبورد',LayoutDashboard],['استراتژی',Compass],['اهداف',Target],['کارت امتیازی',ClipboardCheck],['شاخص‌ها',Gauge],['فرآیندها',Workflow],['ریسک‌ها',ShieldCheck],['ابتکارات',Zap],['پروژه‌ها',FileBarChart],['کارکنان',Users],['سازمان',Network]
] as const;
const trend=[{m:'فروردین',v:68},{m:'اردیبهشت',v:71},{m:'خرداد',v:70},{m:'تیر',v:76},{m:'مرداد',v:78},{m:'شهریور',v:82}];
const perspectives=[{name:'مالی',value:84,color:'#22c55e'},{name:'مشتری',value:76,color:'#14b8a6'},{name:'فرآیندهای داخلی',value:69,color:'#f59e0b'},{name:'یادگیری و رشد',value:73,color:'#6366f1'}];
const alerts=[{title:'حاشیه سود عملیاتی',meta:'کمتر از آستانه هشدار · مالی',sev:'بحرانی',color:'red'},{title:'زمان چرخه تحویل سفارش',meta:'روند نامطلوب در ۳ دوره · عملیات',sev:'نیازمند توجه',color:'amber'},{title:'رضایت مشتریان کلیدی',meta:'داده شهریور ثبت نشده · فروش',sev:'فقدان داده',color:'blue'}];
const entities=[
 {type:'استراتژی',title:'رشد سودآور و پایدار',sub:'STR-1403-01',icon:Compass,color:'purple'},
 {type:'هدف استراتژیک',title:'افزایش سودآوری عملیاتی',sub:'مالک: معاون مالی',icon:Target,color:'indigo'},
 {type:'شاخص کلیدی عملکرد',title:'حاشیه سود عملیاتی',sub:'عملکرد ۱۸.۴٪ از هدف ۲۰٪',icon:Gauge,color:'teal'},
 {type:'فرآیند',title:'برنامه‌ریزی و کنترل تولید',sub:'مالک: مدیر عملیات',icon:Workflow,color:'amber'},
 {type:'ابتکار',title:'بهینه‌سازی سبد محصولات',sub:'پیشرفت ۶۴٪',icon:Zap,color:'blue'},
 {type:'ریسک',title:'افزایش بهای مواد اولیه',sub:'امتیاز ریسک: ۱۶',icon:AlertTriangle,color:'red'}
];

function App(){
 const [active,setActive]=useState('داشبورد'); const [side,setSide]=useState(false); const [query,setQuery]=useState(''); const [period,setPeriod]=useState('سال ۱۴۰۳'); const [toast,setToast]=useState('');
 const shown=useMemo(()=>entities.filter(e=>e.title.includes(query)||e.type.includes(query)),[query]);
 const notify=(t:string)=>{setToast(t);setTimeout(()=>setToast(''),2400)};
 return <div className="app" dir="rtl">
  <aside className={side?'sidebar open':'sidebar'}>
   <div className="brand"><div className="mark"><TrendingUp/></div><div><b>STRATIVA</b><span>از استراتژی تا اجرا</span></div><button className="close" onClick={()=>setSide(false)}><X/></button></div>
   <div className="org"><div className="org-logo">پ</div><div><strong>شرکت نمونه پارس</strong><small>سازمان اصلی</small></div><ChevronDown/></div>
   <nav>{nav.map(([n,I])=><button key={n} className={active===n?'active':''} onClick={()=>{setActive(n);setSide(false);notify(`${n} انتخاب شد`)}}><I/><span>{n}</span>{n==='ریسک‌ها'&&<em>۳</em>}</button>)}</nav>
   <div className="nav-divider"/><button className="nav-foot"><Sparkles/><span>دستیار هوش مصنوعی</span><i>AI</i></button><button className="nav-foot"><Settings/><span>مدیریت سیستم</span></button>
   <div className="user"><div className="avatar">ن.ا</div><div><strong>نازنین احمدی</strong><small>مدیر استراتژی</small></div><button><ChevronDown/></button></div>
  </aside>
  <main>
   <header><button className="mobile-menu" onClick={()=>setSide(true)}><Menu/></button><div className="search"><Search/><input aria-label="جستجو" value={query} onChange={e=>setQuery(e.target.value)} placeholder="جستجو در استراتژی، شاخص، فرآیند..."/><kbd>⌘ K</kbd></div><div className="head-actions"><button onClick={()=>notify('اعلان جدیدی ندارید')}><Bell/><span/></button><button className="primary" onClick={()=>notify('فرم ایجاد آیتم جدید آماده است')}><Plus/> ایجاد جدید</button></div></header>
   <div className="content">
    <section className="intro"><div><p>چهارشنبه، ۱۴ شهریور ۱۴۰۳</p><h1>داشبورد مدیریت استراتژی</h1><span>تصویر یکپارچه‌ای از سلامت استراتژی و عملکرد سازمان</span></div><div className="period"><button onClick={()=>setPeriod(period==='سال ۱۴۰۳'?'سال ۱۴۰۲':'سال ۱۴۰۳')}>{period}<ChevronDown/></button><button className="iconbtn" onClick={()=>notify('گزارش داشبورد آماده شد')}><FileBarChart/></button></div></section>
    <section className="score-grid">
     <div className="health panel"><div className="panel-title"><div><span className="eyebrow">امتیاز سلامت استراتژی</span><b>وضعیت کلی سازمان</b></div><button>جزئیات <ArrowLeft/></button></div><div className="gauge"><svg viewBox="0 0 180 100"><path d="M20 90 A70 70 0 0 1 160 90" pathLength="100"/><path className="fill" d="M20 90 A70 70 0 0 1 160 90" pathLength="100"/></svg><div><strong>۷۸</strong><span>از ۱۰۰</span></div></div><div className="delta"><TrendingUp/> ۶٪ بهبود نسبت به دوره قبل</div></div>
     <div className="metric panel"><div className="metric-icon purple"><Target/></div><div><span>اهداف استراتژیک</span><strong>۲۴</strong><small><b>۱۸</b> هدف در مسیر تحقق</small></div><div className="mini"><i style={{height:'42%'}}/><i style={{height:'55%'}}/><i style={{height:'48%'}}/><i style={{height:'72%'}}/><i style={{height:'82%'}}/></div></div>
     <div className="metric panel"><div className="metric-icon teal"><Gauge/></div><div><span>شاخص‌های فعال</span><strong>۶۸</strong><small><b>۷۴٪</b> در وضعیت مطلوب</small></div><div className="donut">۷۴٪</div></div>
     <div className="metric panel"><div className="metric-icon amber"><Zap/></div><div><span>ابتکارات راهبردی</span><strong>۱۲</strong><small><b>۸</b> ابتکار در حال اجرا</small></div><div className="mini amber-bars"><i style={{height:'30%'}}/><i style={{height:'68%'}}/><i style={{height:'50%'}}/><i style={{height:'78%'}}/><i style={{height:'64%'}}/></div></div>
    </section>
    <section className="middle-grid">
     <div className="panel trend"><div className="panel-title"><div><b>روند عملکرد استراتژیک</b><span>میانگین وزنی تحقق اهداف و شاخص‌ها</span></div><button>۶ ماه اخیر <ChevronDown/></button></div><div className="chart-wrap"><ResponsiveContainer width="100%" height="100%"><AreaChart data={trend}><defs><linearGradient id="grad" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stopColor="#5b5ce2" stopOpacity=".3"/><stop offset="1" stopColor="#5b5ce2" stopOpacity="0"/></linearGradient></defs><CartesianGrid vertical={false} stroke="#e9edf3"/><XAxis dataKey="m" axisLine={false} tickLine={false}/><YAxis orientation="right" axisLine={false} tickLine={false} domain={[50,100]}/><Tooltip/><Area type="monotone" dataKey="v" stroke="#5b5ce2" strokeWidth={3} fill="url(#grad)"/></AreaChart></ResponsiveContainer></div></div>
     <div className="panel perspectives"><div className="panel-title"><div><b>عملکرد منظرهای کارت امتیازی</b><span>بر اساس امتیاز وزنی شاخص‌ها</span></div><button>کارت امتیازی <ArrowLeft/></button></div>{perspectives.map(p=><div className="persp" key={p.name}><div><span>{p.name}</span><strong>{p.value}٪</strong></div><div className="progress"><i style={{width:`${p.value}%`,background:p.color}}/></div></div>)}</div>
    </section>
    <section className="bottom-grid">
     <div className="panel trace"><div className="panel-title"><div><b>زنجیره همسویی استراتژیک</b><span>از استراتژی تا اجرا؛ همه چیز به هم متصل است</span></div><button>نمایش گراف <Network/></button></div><div className="search-inline"><Search/><input value={query} onChange={e=>setQuery(e.target.value)} placeholder="جستجو در زنجیره ارتباطات..."/></div><div className="entity-row">{shown.map((e,i)=><React.Fragment key={e.title}><button className="entity" onClick={()=>notify(`جزئیات «${e.title}» باز شد`)}><span className={`entity-icon ${e.color}`}><e.icon/></span><small>{e.type}</small><strong>{e.title}</strong><em>{e.sub}</em></button>{i<shown.length-1&&<ArrowLeft className="connector"/>}</React.Fragment>)}</div>{shown.length===0&&<div className="empty">موردی با این عبارت پیدا نشد.</div>}</div>
     <div className="panel alerts"><div className="panel-title"><div><b>نیازمند توجه شما</b><span>هشدارها و موارد مهم این دوره</span></div><button>همه موارد <ArrowLeft/></button></div>{alerts.map(a=><button className="alert" key={a.title} onClick={()=>notify(`پیگیری «${a.title}» ایجاد شد`)}><span className={`dot ${a.color}`}/><div><strong>{a.title}</strong><small>{a.meta}</small></div><em className={a.color}>{a.sev}</em><ArrowLeft/></button>)}</div>
    </section>
   </div>
  </main>{side&&<div className="scrim" onClick={()=>setSide(false)}/>} {toast&&<div className="toast"><ClipboardCheck/>{toast}</div>}
 </div>
}
createRoot(document.getElementById('root')!).render(<App/>);
