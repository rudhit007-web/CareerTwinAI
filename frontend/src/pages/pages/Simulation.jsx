import { useState } from 'react'
import toast from 'react-hot-toast'
import { GitCompareArrows, Sparkles } from 'lucide-react'
import { careerAPI } from '../api/client'
import Loader from '../components/Loader'

export default function Simulation(){
  const [a,setA]=useState('AI/ML Engineer'); const [b,setB]=useState('Full Stack Developer'); const [data,setData]=useState(null); const [loading,setLoading]=useState(false)
  const run=async()=>{setLoading(true);try{setData((await careerAPI.simulate({option_a:a,option_b:b})).data);toast.success('Career simulation generated.')}catch(e){toast.error(e.response?.data?.detail||'Simulation failed.')}finally{setLoading(false)}}
  return <div className="space-y-6 animate-fade-in">
    <div><div className="flex items-center gap-2"><GitCompareArrows className="text-ibm-purple" size={22}/><h1 className="text-2xl font-bold text-ibm-white">Career Simulation</h1></div><p className="text-ibm-gray-4 mt-1">Compare two career paths using your current profile and a six-month action plan.</p></div>
    <div className="card grid md:grid-cols-2 gap-4"><div><label className="label">Career path A</label><input className="input" value={a} onChange={e=>setA(e.target.value)}/></div><div><label className="label">Career path B</label><input className="input" value={b} onChange={e=>setB(e.target.value)}/></div><button onClick={run} disabled={loading} className="btn-primary md:col-span-2 flex items-center justify-center gap-2">{loading?<><span className="animate-spin">◌</span>Simulating…</>:<><Sparkles size={15}/>Compare paths</>}</button></div>
    {loading&&<Loader text="Gemini is comparing the two paths…"/>}
    {data&&<div className="space-y-5"><div className="card"><h2 className="font-semibold text-ibm-white mb-4">Comparison</h2><div className="space-y-3">{data.comparison?.map((x,i)=><div key={i} className="grid md:grid-cols-3 gap-2 border-b border-ibm-gray-3 pb-3"><div className="font-medium text-ibm-white">{x.criterion}</div><div className="text-sm text-ibm-gray-4"><b>{a}:</b> {x.a}</div><div className="text-sm text-ibm-gray-4"><b>{b}:</b> {x.b}</div></div>)}</div></div><div className="grid md:grid-cols-2 gap-5"><div className="card"><h3 className="font-semibold text-ibm-white mb-3">6-month plan: {a}</h3><div className="space-y-2 text-sm text-ibm-gray-4">{data.six_month_plan_a?.map((x,i)=><p key={i}><b className="text-ibm-white">{x.month}:</b> {x.goal||x}</p>)}</div></div><div className="card"><h3 className="font-semibold text-ibm-white mb-3">6-month plan: {b}</h3><div className="space-y-2 text-sm text-ibm-gray-4">{data.six_month_plan_b?.map((x,i)=><p key={i}><b className="text-ibm-white">{x.month}:</b> {x.goal||x}</p>)}</div></div></div><div className="card"><h3 className="font-semibold text-ibm-white mb-3">Questions to consider</h3><ul className="list-disc pl-5 text-sm text-ibm-gray-4 space-y-2">{data.decision_questions?.map((x,i)=><li key={i}>{x}</li>)}</ul></div></div>}
  </div>
}
