import {
  FileText,
  FolderOpen,
  Upload,
  Search,
  Filter,
  Download,
  Eye,
  Clock,
  CheckCircle,
  AlertCircle,
  File,
  FileImage,
  FileBadge,
  MoreVertical,
  Plus,
} from 'lucide-react'

const folders = [
  { name: '図面・設計書', count: 142, icon: FolderOpen, color: 'primary' },
  { name: '施工管理書類', count: 87, icon: FolderOpen, color: 'approve' },
  { name: '安全管理書類', count: 63, icon: FolderOpen, color: 'safety' },
  { name: '検査・試験記録', count: 45, icon: FolderOpen, color: 'site' },
  { name: '契約書類', count: 29, icon: FolderOpen, color: 'concrete' },
  { name: '写真台帳', count: 384, icon: FolderOpen, color: 'soil' },
]

const recentDocs = [
  {
    id: 1,
    name: '品川タワー_施工計画書_Rev3.pdf',
    project: '品川タワー新築工事',
    type: 'pdf',
    size: '4.2 MB',
    status: 'approved',
    author: '田中 健一',
    updatedAt: '2024-11-20 14:32',
  },
  {
    id: 2,
    name: '横浜マンション_配筋検査記録.xlsx',
    project: '横浜分譲マンション建設',
    type: 'xlsx',
    size: '1.8 MB',
    status: 'pending',
    author: '鈴木 次郎',
    updatedAt: '2024-11-20 11:15',
  },
  {
    id: 3,
    name: '大田区道路_完成写真帳.zip',
    project: '大田区道路改良工事',
    type: 'zip',
    size: '128 MB',
    status: 'approved',
    author: '佐藤 三郎',
    updatedAt: '2024-11-19 17:48',
  },
  {
    id: 4,
    name: '川崎物流_地盤調査報告書.pdf',
    project: '川崎物流センター建設',
    type: 'pdf',
    size: '8.6 MB',
    status: 'review',
    author: '伊藤 五郎',
    updatedAt: '2024-11-19 09:22',
  },
  {
    id: 5,
    name: '品川タワー_安全パトロール記録_Nov.docx',
    project: '品川タワー新築工事',
    type: 'docx',
    size: '0.9 MB',
    status: 'pending',
    author: '田中 健一',
    updatedAt: '2024-11-18 16:05',
  },
  {
    id: 6,
    name: '横浜マンション_構造計算書.pdf',
    project: '横浜分譲マンション建設',
    type: 'pdf',
    size: '12.4 MB',
    status: 'approved',
    author: '山田 建築士',
    updatedAt: '2024-11-17 10:30',
  },
]

const statusConfig = {
  approved: { label: '承認済', className: 'bg-approve-50 text-approve-700', icon: CheckCircle },
  pending: { label: '承認待', className: 'bg-safety-50 text-safety-700', icon: Clock },
  review: { label: 'レビュー中', className: 'bg-primary-50 text-primary-700', icon: AlertCircle },
}

const fileIconMap: Record<string, React.ElementType> = {
  pdf: FileBadge,
  xlsx: FileText,
  docx: FileText,
  zip: File,
  jpg: FileImage,
  png: FileImage,
}

const fileColorMap: Record<string, string> = {
  pdf: 'text-danger-500',
  xlsx: 'text-approve-600',
  docx: 'text-primary-500',
  zip: 'text-concrete-500',
  jpg: 'text-site-600',
  png: 'text-site-600',
}

export default function DocumentsPage() {
  return (
    <div className="p-6 lg:p-8 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">文書管理</h1>
          <p className="mt-1 text-gray-500 text-sm">建設書類・図面・写真の一元管理と電子承認</p>
        </div>
        <div className="flex gap-2">
          <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
            <Upload className="h-4 w-4" />
            アップロード
          </button>
          <button className="inline-flex items-center gap-2 rounded-lg bg-primary-600 px-4 py-2.5 text-sm font-semibold text-white hover:bg-primary-700 transition-colors">
            <Plus className="h-4 w-4" />
            新規フォルダ
          </button>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
          <p className="text-3xl font-bold text-gray-900">750</p>
          <p className="text-xs text-gray-500 mt-1">総ファイル数</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
          <p className="text-3xl font-bold text-safety-600">12</p>
          <p className="text-xs text-gray-500 mt-1">承認待ち</p>
        </div>
        <div className="rounded-xl border border-gray-200 bg-white p-4 text-center">
          <p className="text-3xl font-bold text-primary-600">4.8 GB</p>
          <p className="text-xs text-gray-500 mt-1">使用容量</p>
        </div>
      </div>

      {/* Search */}
      <div className="flex gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <input
            type="text"
            placeholder="ファイル名・工事名・種類で検索..."
            className="w-full rounded-lg border border-gray-200 bg-white pl-10 pr-4 py-2.5 text-sm focus:border-primary-500 focus:outline-none focus:ring-2 focus:ring-primary-500/20"
          />
        </div>
        <button className="inline-flex items-center gap-2 rounded-lg border border-gray-200 bg-white px-4 py-2.5 text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors">
          <Filter className="h-4 w-4" />
          フィルター
        </button>
      </div>

      {/* Folder Grid */}
      <div>
        <h2 className="text-sm font-semibold text-gray-700 mb-3">フォルダ</h2>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
          {folders.map((folder) => {
            const Icon = folder.icon
            return (
              <button
                key={folder.name}
                className="flex flex-col items-center gap-2 rounded-xl border border-gray-200 bg-white p-4 hover:border-primary-300 hover:shadow-sm transition-all text-center group"
              >
                <Icon className={`h-8 w-8 text-${folder.color}-500 group-hover:text-${folder.color}-600`} />
                <span className="text-xs font-medium text-gray-700 leading-tight">{folder.name}</span>
                <span className="text-xs text-gray-400">{folder.count}件</span>
              </button>
            )
          })}
        </div>
      </div>

      {/* Recent Documents */}
      <div className="rounded-xl border border-gray-200 bg-white overflow-hidden">
        <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100">
          <h2 className="font-bold text-gray-900">最近の書類</h2>
          <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">すべて表示</button>
        </div>
        <table className="min-w-full divide-y divide-gray-100">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-5 py-3 text-left text-xs font-semibold text-gray-500">ファイル名</th>
              <th className="hidden md:table-cell px-5 py-3 text-left text-xs font-semibold text-gray-500">工事</th>
              <th className="px-5 py-3 text-left text-xs font-semibold text-gray-500">ステータス</th>
              <th className="hidden lg:table-cell px-5 py-3 text-left text-xs font-semibold text-gray-500">更新日時</th>
              <th className="hidden lg:table-cell px-5 py-3 text-left text-xs font-semibold text-gray-500">サイズ</th>
              <th className="px-5 py-3"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {recentDocs.map((doc) => {
              const FileIcon = fileIconMap[doc.type] || File
              const fileColor = fileColorMap[doc.type] || 'text-gray-400'
              const status = statusConfig[doc.status as keyof typeof statusConfig]
              const StatusIcon = status.icon
              return (
                <tr key={doc.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-3">
                      <FileIcon className={`h-5 w-5 ${fileColor} flex-shrink-0`} />
                      <span className="text-sm font-medium text-gray-800 truncate max-w-[200px]">{doc.name}</span>
                    </div>
                  </td>
                  <td className="hidden md:table-cell px-5 py-3.5">
                    <span className="text-sm text-gray-600">{doc.project}</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-medium ${status.className}`}>
                      <StatusIcon className="h-3 w-3" />
                      {status.label}
                    </span>
                  </td>
                  <td className="hidden lg:table-cell px-5 py-3.5">
                    <span className="text-xs text-gray-500">{doc.updatedAt}</span>
                  </td>
                  <td className="hidden lg:table-cell px-5 py-3.5">
                    <span className="text-xs text-gray-500">{doc.size}</span>
                  </td>
                  <td className="px-5 py-3.5">
                    <div className="flex items-center gap-1">
                      <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors">
                        <Eye className="h-3.5 w-3.5" />
                      </button>
                      <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors">
                        <Download className="h-3.5 w-3.5" />
                      </button>
                      <button className="p-1.5 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded transition-colors">
                        <MoreVertical className="h-3.5 w-3.5" />
                      </button>
                    </div>
                  </td>
                </tr>
              )
            })}
          </tbody>
        </table>
      </div>
    </div>
  )
}
