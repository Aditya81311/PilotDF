import { useState, useEffect } from 'react'
import api from '../api/axios'
import { Upload, FileText, Grid, AlertTriangle, CheckCircle, XCircle, RefreshCw } from 'lucide-react'

export default function Dashboard() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [uploading, setUploading] = useState(false)
  const [error, setError] = useState('')
  const [dragOver, setDragOver] = useState(false)

  const fetchDashboard = async () => {
    setLoading(true)
    try {
      const res = await api.get('/dashboard')
      setData(res.data)
      setError('')
    } catch (err) {
      if (err.response?.status === 404) setData(null)
      else setError(err.response?.data?.error || 'Failed to load dashboard')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { fetchDashboard() }, [])

  const handleUpload = async (file) => {
    if (!file) return
    const allowed = ['csv', 'xlsx', 'xls']
    const ext = file.name.split('.').pop().toLowerCase()
    if (!allowed.includes(ext)) {
      setError('Only CSV and Excel files are supported')
      return
    }
    setUploading(true)
    setError('')
    const formData = new FormData()
    formData.append('file', file)
    try {
      await api.post('/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      await fetchDashboard()
    } catch (err) {
      setError(err.response?.data?.error || 'Upload failed')
    } finally {
      setUploading(false)
    }
  }

  const handleReset = async () => {
    try {
      await api.post('/reset')
      await fetchDashboard()
    } catch (err) {
      setError(err.response?.data?.error || 'Reset failed')
    }
  }

  const healthColor = {
    ok:   'text-green-400',
    warn: 'text-yellow-400',
    bad:  'text-red-400',
  }

  const healthIcon = {
    ok:   <CheckCircle size={20} className="text-green-400" />,
    warn: <AlertTriangle size={20} className="text-yellow-400" />,
    bad:  <XCircle size={20} className="text-red-400" />,
  }

  if (loading) return (
    <div className="min-h-screen bg-gray-950 flex items-center justify-center">
      <div className="w-8 h-8 border-2 border-[#534AB7] border-t-transparent rounded-full animate-spin" />
    </div>
  )

  // No file uploaded — show upload screen
  if (!data) return (
    <div className="min-h-screen bg-gray-950 flex flex-col items-center justify-center px-4">
      <div className="w-full max-w-lg">
        <h2 className="text-2xl font-bold text-white mb-2">Upload a File</h2>
        <p className="text-gray-400 text-sm mb-8">CSV, XLSX or XLS — max 50MB</p>

        {error && (
          <div className="mb-4 text-sm text-red-400 bg-red-950 border border-red-800 rounded-lg px-4 py-3">
            {error}
          </div>
        )}

        <label
          onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
          onDragLeave={() => setDragOver(false)}
          onDrop={(e) => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files[0]) }}
          className={`flex flex-col items-center justify-center w-full h-56 border-2 border-dashed rounded-2xl cursor-pointer transition-colors
            ${dragOver ? 'border-[#534AB7] bg-[#534AB7]/10' : 'border-gray-700 bg-gray-900 hover:border-[#534AB7]'}`}
        >
          {uploading ? (
            <div className="w-8 h-8 border-2 border-[#534AB7] border-t-transparent rounded-full animate-spin" />
          ) : (
            <>
              <Upload size={36} className="text-gray-500 mb-3" />
              <p className="text-gray-400 text-sm">Drag & drop or <span className="text-[#534AB7]">browse</span></p>
            </>
          )}
          <input type="file" className="hidden" accept=".csv,.xlsx,.xls"
            onChange={(e) => handleUpload(e.target.files[0])} />
        </label>
      </div>
    </div>
  )

  // File loaded — show dashboard
  return (
    <div className="p-6 space-y-6 bg-gray-950 min-h-screen">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold text-white">{data.file_name}</h2>
          <p className="text-gray-400 text-sm">{data.file_size} · {data.memory_size} in memory</p>
        </div>
        <div className="flex gap-3">
          <button onClick={handleReset}
            className="flex items-center gap-2 px-4 py-2 text-sm bg-gray-800 hover:bg-gray-700 text-gray-300 rounded-lg transition-colors">
            <RefreshCw size={15} /> Reset
          </button>
          <label className="flex items-center gap-2 px-4 py-2 text-sm bg-[#534AB7] hover:bg-[#4540a0] text-white rounded-lg cursor-pointer transition-colors">
            <Upload size={15} /> New File
            <input type="file" className="hidden" accept=".csv,.xlsx,.xls"
              onChange={(e) => handleUpload(e.target.files[0])} />
          </label>
        </div>
      </div>

      {error && (
        <div className="text-sm text-red-400 bg-red-950 border border-red-800 rounded-lg px-4 py-3">
          {error}
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {[
          { label: 'Rows',       value: data.rows },
          { label: 'Columns',    value: data.columns },
          { label: 'Null %',     value: `${data.null_pct}%` },
          { label: 'Duplicates', value: data.duplicate_rows },
        ].map(({ label, value }) => (
          <div key={label} className="bg-gray-900 rounded-xl p-4 border border-gray-800">
            <p className="text-gray-400 text-xs mb-1">{label}</p>
            <p className="text-2xl font-bold text-white">{value}</p>
          </div>
        ))}
      </div>

      {/* Health + Issues */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
          <div className="flex items-center gap-2 mb-4">
            {healthIcon[data.health_status]}
            <h3 className="text-white font-semibold">Data Health</h3>
            <span className={`text-sm font-medium ml-auto ${healthColor[data.health_status]}`}>
              {data.health_status.toUpperCase()}
            </span>
          </div>
          <ul className="space-y-2">
            {data.issues.map((issue, i) => (
              <li key={i} className="flex items-start gap-2 text-sm">
                {issue.type === 'ok'
                  ? <CheckCircle size={14} className="text-green-400 mt-0.5 shrink-0" />
                  : <AlertTriangle size={14} className="text-yellow-400 mt-0.5 shrink-0" />}
                <span className="text-gray-300">{issue.message}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Column Overview */}
        <div className="bg-gray-900 rounded-xl p-5 border border-gray-800">
          <div className="flex items-center gap-2 mb-4">
            <Grid size={18} className="text-[#534AB7]" />
            <h3 className="text-white font-semibold">Column Overview</h3>
          </div>
          <div className="overflow-auto max-h-56">
            <table className="w-full text-sm">
              <thead>
                <tr className="text-gray-500 text-xs border-b border-gray-800">
                  <th className="text-left pb-2">Name</th>
                  <th className="text-left pb-2">Type</th>
                  <th className="text-left pb-2">Nulls</th>
                  <th className="text-left pb-2">Unique</th>
                </tr>
              </thead>
              <tbody>
                {data.overview.map((col, i) => (
                  <tr key={i} className="border-b border-gray-800/50 text-gray-300">
                    <td className="py-1.5 pr-3 font-medium truncate max-w-[120px]">{col.name}</td>
                    <td className="py-1.5 pr-3">
                      <span className="text-xs bg-gray-800 px-2 py-0.5 rounded text-[#534AB7]">{col.type}</span>
                    </td>
                    <td className="py-1.5 pr-3">{col.null_pct}%</td>
                    <td className="py-1.5">{col.unique}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </div>
  )
}