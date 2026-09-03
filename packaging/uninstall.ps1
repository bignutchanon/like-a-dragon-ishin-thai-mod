# ตัวถอนม็อดแปลไทย Like a Dragon: Ishin! (ISHTH)
# ลบไฟล์ .pak ของม็อดออกจากโฟลเดอร์ ~mods — ไฟล์เกมต้นฉบับไม่เคยถูกแตะ จึงไม่ต้องคืนอะไร

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

$exeRel = 'LikeaDragonIshin\Binaries\Win64\LikeaDragonIshin-Win64-Shipping.exe'

function Find-Game {
    $cands = @()
    $steam = (Get-ItemProperty 'HKCU:\Software\Valve\Steam' -ErrorAction SilentlyContinue).SteamPath
    if ($steam) {
        $cands += $steam
        $vdf = Join-Path $steam 'steamapps\libraryfolders.vdf'
        if (Test-Path $vdf) {
            foreach ($m in (Select-String -Path $vdf -Pattern '"path"\s*"(.+?)"' -AllMatches).Matches) {
                $cands += $m.Groups[1].Value -replace '\\', '\'
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
Write-Host '=== ม็อดแปลไทย Like a Dragon: Ishin! (ISHTH) — ถอนการติดตั้ง ===' -ForegroundColor Cyan
Write-Host ''

$game = Find-Game
if (-not $game) {
    Write-Host 'หาโฟลเดอร์เกมอัตโนมัติไม่เจอ' -ForegroundColor Yellow
    Write-Host 'ให้วางพาธของโฟลเดอร์เกม (โฟลเดอร์ที่มี startup.exe และโฟลเดอร์ LikeaDragonIshin)'
    $inp = (Read-Host 'พาธ').Trim()
    $inp = $inp.Trim([char]34)
    if (Test-Path (Join-Path $inp $exeRel)) { $game = $inp }
    else { Write-Host 'พาธไม่ถูกต้อง — ยกเลิก' -ForegroundColor Red; exit 1 }
}
Write-Host ("พบเกมที่: " + $game)

$mods = Join-Path $game 'LikeaDragonIshin\Content\Paks\~mods'
$n = 0
if (Test-Path $mods) {
    $old = Get-ChildItem $mods -File |
           Where-Object { $_.Name -like 'IshinThai*_P.pak' -or $_.Name -eq 'LikeADragonIshinThai_P.pak' }
    foreach ($f in $old) {
        Remove-Item $f.FullName -Force
        Write-Host ('  ลบแล้ว: ~mods\' + $f.Name)
        $n++
    }
}
if ($n -eq 0) { Write-Host '  ไม่พบไฟล์ม็อดใน ~mods (อาจถอนไปแล้ว)' -ForegroundColor Yellow }

Write-Host ''
Write-Host 'ถอนการติดตั้งเสร็จแล้ว' -ForegroundColor Green
Write-Host ''
