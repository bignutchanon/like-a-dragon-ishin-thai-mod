# วางชุดเซฟทดสอบ (work/saves/community_legend) ลงโฟลเดอร์เซฟของ Like a Dragon: Ishin!
# - สำรองสล็อตเดิมทั้งหมดไว้ที่ work/saves/backup_<เวลา>/ ก่อนเสมอ
# - ไม่แตะ system/ กับ steam_autocloud.vdf ของผู้ใช้
# - ปิด Steam Cloud ของเกมก่อนรัน ไม่งั้นคลาวด์จะดึงของเดิมกลับมาทับ
param([string]$UserId = "162221971")
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$src  = Join-Path $root "work\saves\community_legend"
$dst  = Join-Path $env:APPDATA "SEGA\LikeADragonIshin\$UserId"
if (-not (Test-Path $src)) { throw "ไม่พบ $src" }
if (-not (Test-Path $dst)) { throw "ไม่พบโฟลเดอร์เซฟของเกม $dst (เปิดเกมสักครั้งให้มันสร้างก่อน)" }

$stamp  = Get-Date -Format "yyyyMMdd_HHmmss"
$backup = Join-Path $root "work\saves\backup_$stamp"
$existing = Get-ChildItem $dst -Directory | Where-Object { $_.Name -like "save00*" }
if ($existing) {
    New-Item -ItemType Directory -Force $backup | Out-Null
    foreach ($d in $existing) { Copy-Item $d.FullName (Join-Path $backup $d.Name) -Recurse -Force }
    Write-Host ("สำรองสล็อตเดิม {0} สล็อต -> {1}" -f $existing.Count, $backup)
} else { Write-Host "ไม่มีสล็อตเดิม ไม่ต้องสำรอง" }

$slots = Get-ChildItem $src -Directory | Where-Object { $_.Name -like "save00*" }
foreach ($s in $slots) {
    $target = Join-Path $dst $s.Name
    if (Test-Path $target) { Remove-Item $target -Recurse -Force -Confirm:$false }
    Copy-Item $s.FullName $target -Recurse -Force
}
Write-Host ("วางเซฟทดสอบ {0} สล็อต -> {1}" -f $slots.Count, $dst)
Write-Host "รายละเอียดสล็อต: work\saves\README.md · ก่อนเปิดเกมตรวจว่า Steam Cloud ของเกมปิดอยู่"
