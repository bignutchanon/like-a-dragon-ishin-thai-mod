# ตัวติดตั้งม็อดแปลไทย Like a Dragon: Ishin! (ISHTH)
# ภาคนี้เป็น Unreal Engine 4 — ม็อดเป็นไฟล์ .pak ไฟล์เดียว วางในโฟลเดอร์ ~mods ของเกม
# ไม่เขียนทับไฟล์ต้นฉบับของเกมสักไฟล์ · ถอนได้ด้วยการลบไฟล์ .pak ออก

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$pakSrc = Join-Path $root 'files\IshinThai_P.pak'

$exeRel = 'LikeaDragonIshin\Binaries\Win64\LikeaDragonIshin-Win64-Shipping.exe'

function Find-Game {
    $cands = @()
    $steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue).SteamPath
    if ($steam) {
        $cands += $steam
        $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
        if (Test-Path $vdf) {
            foreach ($m in (Select-String -Path $vdf -Pattern '"path"\s*"(.+?)"' -AllMatches).Matches) {
                $cands += $m.Groups[1].Value -replace '\\', '\'   # VDF เขียน path ด้วยแบ็กสแลชคู่
            }
        }
    }
    $cands += 'C:\Program Files (x86)\Steam'
    foreach ($c in $cands) {
        $p = Join-Path $c 'steamapps\common\LikeADragonIshin'
        if (Test-Path (Join-Path $p $exeRel)) { return $p }
    }
    return $null
}

Write-Host ''
Write-Host '=== ม็อดแปลไทย Like a Dragon: Ishin! (ISHTH) — ตัวติดตั้ง ===' -ForegroundColor Cyan
Write-Host ''

if (-not (Test-Path $pakSrc)) {
    Write-Host 'ไม่พบ files\IshinThai_P.pak ในชุดติดตั้ง — แตกไฟล์ zip ให้ครบก่อน' -ForegroundColor Red
    exit 1
}

$game = Find-Game
if (-not $game) {
    Write-Host 'หาโฟลเดอร์เกมอัตโนมัติไม่เจอ' -ForegroundColor Yellow
    Write-Host 'ให้วางพาธของโฟลเดอร์เกม (โฟลเดอร์ที่มี startup.exe และโฟลเดอร์ LikeaDragonIshin)'
    Write-Host 'ปกติอยู่ที่  ...\steamapps\common\LikeADragonIshin'
    $inp = (Read-Host 'พาธ').Trim()
    $inp = $inp.Trim([char]34)
    if (Test-Path (Join-Path $inp $exeRel)) { $game = $inp }
    else { Write-Host 'พาธไม่ถูกต้อง — ยกเลิก' -ForegroundColor Red; exit 1 }
}
Write-Host ("พบเกมที่: " + $game)

# ---- วาง .pak ลง ~mods (ลบเวอร์ชันเก่าของม็อดนี้ก่อน) ----
$mods = Join-Path $game 'LikeaDragonIshin\Content\Paks\~mods'
New-Item -ItemType Directory -Force -Path $mods | Out-Null
$old = Get-ChildItem $mods -File -ErrorAction SilentlyContinue |
       Where-Object { $_.Name -like 'IshinThai*_P.pak' -or $_.Name -eq 'LikeADragonIshinThai_P.pak' }
foreach ($f in $old) {
    Remove-Item $f.FullName -Force
    Write-Host ('  ลบเวอร์ชันเก่า: ' + $f.Name)
}
Copy-Item $pakSrc (Join-Path $mods 'IshinThai_P.pak') -Force
$size = [math]::Round((Get-Item (Join-Path $mods 'IshinThai_P.pak')).Length / 1MB, 1)
Write-Host ('  ติดตั้งแล้ว: ~mods\IshinThai_P.pak (' + $size + ' MB)')

Write-Host ''
Write-Host 'ติดตั้งเสร็จแล้ว' -ForegroundColor Green
Write-Host 'เข้าเกมแล้วตั้งค่าภาษาข้อความเป็น English — ม็อดเขียนภาษาไทยทับช่องภาษาอังกฤษ'
Write-Host 'ปุ่มเปิดเมนูหยุดเกมบนคีย์บอร์ดของภาคนี้คือ M (ESC ใช้ไม่ได้ตั้งแต่เกมต้นฉบับ)'
Write-Host ''
