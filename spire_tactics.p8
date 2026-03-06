pico-8 cartridge // http://www.pico-8.com/version 42
version 42
__lua__
-- spire tactics
-- roguelike auto-battler

-- parse pipe-delimited data
function pd(s)
 local t={}
 for r in all(split(s,"|")) do
  add(t,split(r,","))
 end
 return t
end
function n(v) return v+0 end
function _has(t,v)
 for x in all(t) do if x==v then return true end end
 return false
end

-- v2 data tables
-- jobs: name,hp,atk,def,spd,pos,tier,parent
-- pos:0=front,1=mid,2=back tier:1/2 parent:0=base
_j=pd("sqr,12,4,3,3,0,1,0|sct,8,3,1,6,2,1,0|aco,9,2,2,4,2,1,0|apr,7,5,1,4,2,1,0|brl,15,3,2,3,0,1,0|lnc,10,4,2,4,1,1,0|knt,16,4,5,2,0,2,1|sam,11,6,2,4,0,2,1|rng,9,5,1,5,2,2,2|thf,8,4,1,7,2,2,2|pst,10,3,3,3,2,2,3|orc,9,2,2,5,2,2,3|blm,7,7,1,3,2,2,4|tmg,8,4,1,5,2,2,4|mnk,16,4,3,4,0,2,5|zrk,14,5,1,3,0,2,5|drg,11,6,2,3,1,2,6|vlk,10,4,3,4,1,2,6")
-- skills: name,jid,type,pw,rng,cd,xtra,dur
-- type:a=atk A=aoe h=heal H=aoeh b=buf1
-- B=bufA d=deb1 D=debA p=prc l=lfs c=ctr
-- pw: x10 mult(atk/heal) or %/flat(buf)
_s=pd("slash,1,a,10,1,0,0,0|guard,1,b,50,0,3,d,2|rally,1,B,1,0,4,s,3|shot,2,a,10,3,0,0,0|dash,2,b,3,0,2,s,2|mark,2,d,50,3,3,m,2|mend,3,h,15,3,1,0,0|bless,3,b,30,3,3,a,3|light,3,a,8,2,0,0,0|fire,4,a,12,3,1,0,0|spark,4,a,7,3,2,0,0|barrir,4,b,15,0,4,h,2|pummel,5,a,10,1,0,0,0|endure,5,h,25,0,3,0,0|roar,5,D,20,0,4,a,2|thrust,6,a,10,2,0,0,0|leap,6,a,13,3,3,0,0|inspre,6,b,20,1,3,a,2|shdwal,7,b,50,1,3,d,2|taunt,7,D,0,0,4,t,2|fortre,7,b,100,0,5,d,3|iaistk,8,a,20,1,3,0,0|blddnc,8,A,7,1,3,0,0|focus,8,b,200,0,4,a,1|volley,9,A,6,3,3,0,0|snipe,9,p,25,3,4,0,0|trap,9,a,15,2,3,w,3|poison,10,d,3,2,2,p,4|steal,10,d,0,1,4,0,0|ambush,10,p,20,1,3,0,0|healal,11,H,10,0,4,0,0|revive,11,h,30,3,6,r,0|holy,11,a,15,3,3,k,0|haste,12,b,3,3,3,s,3|shell,12,b,20,3,3,h,1|forsit,12,B,30,0,5,d,2|firaga,13,A,10,3,4,0,0|thundr,13,a,15,3,3,0,0|drain,13,l,10,2,3,0,0|slow,14,d,3,3,3,s,3|quick,14,b,0,3,3,q,0|comet,14,a,20,3,5,0,0|countr,15,c,100,0,2,0,1|chiwav,15,H,10,0,4,0,0|irnfst,15,p,15,1,2,0,0|frenzy,16,b,2,0,3,a,0|drnstk,16,l,12,1,2,0,0|rampag,16,A,8,1,4,0,0|jump,17,a,20,3,4,j,0|lncchr,17,p,12,2,2,0,0|rend,17,a,10,2,2,d,3|warcry,18,B,30,0,4,a,2|shlbsh,18,a,10,1,2,n,0|aegis,18,b,50,1,3,d,2")
-- accessories: name,stat,bonus,special
_a=pd("pwr glv,a,3,0|irn shd,d,3,0|sprint,s,2,0|hp bngl,h,5,0|ctr rng,0,0,c|heal rd,0,0,h|fcs bnd,0,0,f|wrd chm,0,0,w|hst bch,0,0,b|vmp fng,0,0,v|mag rng,0,0,m|lck chm,0,0,l")
-- potions: name,effect,power,cost
_p=pd("potion,h,50,30|hi-pot,h,100,60|ether,e,0,50|haste,s,100,40|bomb,d,8,45|smoke,n,0,55|phoenx,r,25,75|shield,t,50,40")
-- enemies: name,spr,hp,atk,spd,behavior,def
_e=pd("slime,5,10,4,2,0,2|goblin,6,12,5,3,0,2|wolf,7,9,5,6,1,1|archer,32,8,4,4,2,1|mage,33,7,6,3,3,1|golem,34,18,3,1,5,5|bandit,35,10,5,5,4,2|bat,36,5,3,7,5,0|orc,37,16,6,2,0,3|snake,38,8,4,5,6,1|champ,39,22,7,3,7,4|assassn,40,14,8,6,1,1|shaman,41,16,5,4,8,2|ogre,42,28,8,2,0,3|drake,43,20,7,3,3,4")
-- bosses: name,spr,hp,atk,spd,behavior,def,mechanic
_b=pd("warlrd,44,35,7,3,0,4,s|hydra,45,50,8,4,0,3,m|lich,46,60,10,3,3,5,c")
-- name pool + display names
_nm=split("aria,kael,lira,voss,rhen,dahl,mira,thane")
jn=split("squire,scout,acolyte,apprntc,brawler,lancer,knight,samurai,ranger,thief,priest,oracle,blk mag,time mg,monk,brsrkr,dragoon,valkyri")

function _init()
 cartdata("spiretactics")
 gs="title"
 t=0
 py={}
 gold=0
 pots={}
 rls={}
 fl=1
 mxfl=3
 cfm=false
end

function dcfm()
 if cfm then
  rectfill(20,58,108,68,0)
  rect(20,58,108,68,7)
  print("\x97 confirm  \x96 cancel",24,61,7)
 end
end

-- discovery: bit n = class n discovered
function disc(ji)
 -- mark class as discovered
 local v=dget(0)
 v=bor(v,shl(1,ji-1))
 dset(0,v)
end

function isdisc(ji)
 -- check if class discovered
 return band(dget(0),shl(1,ji-1))!=0
end

function init_draft()
 gs="draft"
 py={}
 -- offer 5 of 6 base classes
 local pool={1,2,3,4,5,6}
 deli(pool,1+flr(rnd(6)))
 dpool=pool
 dpick={}
 sel=1
end

function updraft()
 if btnp(0) then sel=max(1,sel-1) sfx(2) cfm=false end
 if btnp(1) then sel=min(#dpool,sel+1) sfx(2) cfm=false end
 if cfm then
  if btnp(5) then
   cfm=false
   local ji=dpool[sel]
   if not _has(dpick,ji) then
    add(dpick,ji)
    add(py,mku(ji))
    disc(ji)
    sfx(1)
    if #dpick>=3 then
     init_equip()
    end
   end
  elseif btnp(4) then cfm=false sfx(3) end
 elseif btnp(5) and sel<=#dpool then
  cfm=true
 end
end

-- starting equipment selection
function init_equip()
 gs="equip"
 eq_pots={}
 for i=1,3 do add(eq_pots,1+flr(rnd(#_p))) end
 eq_accs={}
 for i=1,3 do add(eq_accs,1+flr(rnd(#_a))) end
 eq_phase=1 sel=1 eq_unit=1
 cfm=false
end

function upequip()
 if eq_phase==1 then
  -- pick a starting potion
  if btnp(2) then sel=max(1,sel-1) sfx(2) end
  if btnp(3) then sel=min(3,sel+1) sfx(2) end
  if btnp(5) then
   add(pots,eq_pots[sel])
   eq_phase=2 sel=1 sfx(1)
  end
 elseif eq_phase==2 then
  -- pick accessory for each unit
  if btnp(2) then sel=max(1,sel-1) sfx(2) end
  if btnp(3) then sel=min(3,sel+1) sfx(2) end
  if btnp(5) then
   py[eq_unit].acc=eq_accs[sel]
   eq_unit+=1 sfx(1)
   -- reroll accessories for next unit
   eq_accs={}
   for i=1,3 do add(eq_accs,1+flr(rnd(#_a))) end
   sel=1
   if eq_unit>3 then
    genmap() gs="map"
   end
  end
 end
end

function dequip()
 rectfill(4,4,124,124,0)
 rect(4,4,124,124,6)
 if eq_phase==1 then
  print("choose starting potion",10,8,11)
  for i=1,3 do
   local p=_p[eq_pots[i]]
   local y=22+(i-1)*20
   local c=i==sel and 10 or 6
   if i==sel then print(">",8,y,10) end
   print(p[1],16,y,c)
   print(p[2],16,y+8,5)
  end
 else
  print("equip "..py[eq_unit].nm,10,8,11)
  print("choose accessory",10,16,6)
  for i=1,3 do
   local a=_a[eq_accs[i]]
   local y=28+(i-1)*20
   local c=i==sel and 10 or 6
   if i==sel then print(">",8,y,10) end
   print(a[1],16,y,c)
   print(a[2],16,y+8,5)
  end
  -- show party so far
  for i=1,3 do
   local u=py[i]
   local y=92+(i-1)*10
   spr(u.ji,8,y)
   print(u.nm,18,y,i<eq_unit and 11 or 5)
   if u.acc then print(_a[u.acc][1],60,y,10) end
  end
 end
 print("\x97 pick",50,118,5)
end

-- v2 unit: named, with tier + kept skill
function mku(ji)
 local j=_j[ji]
 local nm=_nm[1+flr(rnd(#_nm))]
 return{ji=ji,nm=nm,
  hp=n(j[2]),mhp=n(j[2]),
  atk=n(j[3]),def=n(j[4]),spd=n(j[5]),
  tier=1,base=ji,kept=nil,acc=nil,
  x=0,y=0,atb=0,
  cd={0,0,0},alive=true,tm=1,
  slv={1,1,1},
  buffs={},debuffs={}}
end

-- advance unit to tier 2
-- branch: index into _j (7-18)
-- kidx: which current skill to keep (1-3)
function advu(u,branch,kidx)
 local j=_j[branch]
 if n(j[7])!=2 then return end
 -- save kept skill + its level
 local sks=getsk(u.ji)
 local klv=u.slv[min(kidx,3)]
 if kidx>=1 and kidx<=#sks then
  u.kept=sks[kidx]
 end
 u.ji=branch
 u.tier=2
 u.hp=n(j[2])
 u.mhp=n(j[2])
 u.atk=n(j[3])
 u.def=n(j[4])
 u.spd=n(j[5])
 u.cd={0,0,0,0}
 -- new skills at lv1, kept skill keeps its level
 local nsks=getsk(branch)
 u.slv={1,1,1}
 if u.kept then u.slv[min(#nsks+1,3)]=klv end
 disc(branch)
end

-- get skills for a job id
function getsk(ji)
 local r={}
 for s in all(_s) do
  if n(s[2])==ji then add(r,s) end
 end
 return r
end

-- get active skills for unit
-- (kept skill + current class skills)
function ugetsk(u)
 local r={}
 if u.kept then add(r,u.kept) end
 for s in all(getsk(u.ji)) do
  add(r,s)
 end
 return r
end

-- get advancement options for a base class
function advopt(ji)
 local r={}
 for i=1,#_j do
  if n(_j[i][7])==2 and n(_j[i][8])==ji then
   add(r,i)
  end
 end
 return r
end

function mke(ei,x,y)
 local e=_e[ei]
 return{nm=e[1],spr=n(e[2]),
  hp=n(e[3]),mhp=n(e[3]),
  atk=n(e[4]),spd=n(e[5]),
  bf=n(e[6]),def=n(e[7]),
  x=x,y=y,atb=0,alive=true,tm=2,
  ji=0,cd={0,0,0},
  buffs={},debuffs={}}
end

function isopen(nx,ny,u)
 for o in all(py) do
  if o.alive and o!=u and o.x==nx and o.y==ny then return false end
 end
 for o in all(ens) do
  if o.alive and o!=u and o.x==nx and o.y==ny then return false end
 end
 return nx>=0 and nx<=5 and ny>=0 and ny<=3
end

-- map gen
function genmap()
 -- v2: 6 rows, StS layout
 -- tp: 0=start 1=battle 2=elite
 --     3=camp 4=boss 5=shop
 nds={}
 cnod=nil
 local br={}
 for row=0,5 do
  br[row]={}
  local nc
  if row==0 then nc=3
  elseif row==2 then nc=2
  elseif row==5 then nc=1
  else nc=3+flr(rnd(2))
  end
  for i=1,nc do
   local nd={
    row=row,col=i,nc=nc,
    x=flr(20+88/(nc+1)*i),
    y=6+row*16,
    tp=1,cn={},dn=false
   }
   if row==0 then nd.tp=0
   elseif row==5 then nd.tp=4 end
   add(nds,nd)
   add(br[row],nd)
  end
 end
 -- structural guarantees
 -- 2 campfires: rows 1,4
 br[1][1+flr(rnd(#br[1]))].tp=3
 br[4][1+flr(rnd(#br[4]))].tp=3
 -- 2 elites: rows 3,4
 br[3][1+flr(rnd(#br[3]))].tp=2
 for nd in all(br[4]) do
  if nd.tp==1 then nd.tp=2 break end
 end
 -- 1 shop: row 1 or 3
 local sr=rnd(1)<0.5 and 1 or 3
 for nd in all(br[sr]) do
  if nd.tp==1 then nd.tp=5 break end
 end
 -- connect: proximity-based
 for nd in all(nds) do
  if nd.row<5 then
   for n2 in all(nds) do
    if n2.row==nd.row+1 then
     local d=abs(nd.col/(nd.nc+1)
      -n2.col/(n2.nc+1))
     if d<0.4 or rnd(1)<0.15 then
      add(nd.cn,n2)
     end
    end
   end
   if #nd.cn==0 then
    for n2 in all(nds) do
     if n2.row==nd.row+1 then
      add(nd.cn,n2) break
     end
    end
   end
  end
 end
 -- ensure all nodes reachable
 for row=1,5 do
  for nd in all(br[row]) do
   local ok=false
   for pn in all(br[row-1]) do
    if _has(pn.cn,nd) then
     ok=true break
    end
   end
   if not ok then
    add(br[row-1][1].cn,nd)
   end
  end
 end
 cnod=br[0][1]
 cnod.dn=true
 sel=1
end

-- setup
cur={x=0,y=0}
selu=1

function gen_ens()
 ens={}
 if cnod.tp==4 then
  -- boss: use _b table
  local bi=min(fl,#_b)
  local b=_b[bi]
  local e=mke(1,4,1)
  e.nm=b[1] e.spr=n(b[2])
  e.hp=n(b[3]) e.mhp=e.hp
  e.atk=n(b[4]) e.spd=n(b[5])
  e.def=n(b[7])
  add(ens,e)
  local ne=1+flr(rnd(2))
  for i=1,ne do
   local ei=min(1+flr(rnd(5)),10)
   local e=mke(ei,4+flr(rnd(2)),min(i+1,3))
   for o in all(ens) do
    if o.x==e.x and o.y==e.y then e.y=min(e.y+1,3) end
   end
   add(ens,e)
  end
 elseif cnod.tp==2 then
  -- elite: pick from elite pool (11-15)
  local ne=1+flr(rnd(2))
  for i=1,ne do
   local ei=11+flr(rnd(5))
   local e=mke(min(ei,#_e),4+flr(rnd(2)),i-1)
   for o in all(ens) do
    if o.x==e.x and o.y==e.y then e.y=min(e.y+1,3) end
   end
   add(ens,e)
  end
 else
  -- regular: pick from 1-10
  local ne=min(2+flr(fl*0.7),4)
  for i=1,ne do
   local ei=1+flr(rnd(min(3+fl*2,10)))
   local e=mke(min(ei,#_e),4+flr(rnd(2)),i-1)
   e.hp=flr(e.hp*(0.7+fl*0.3))
   e.mhp=e.hp
   e.atk=flr(e.atk*(0.8+fl*0.2))
   for o in all(ens) do
    if o.x==e.x and o.y==e.y then e.y=min(e.y+1,3) end
   end
   add(ens,e)
  end
 end
end

function init_setup()
 gs="setup"
 gen_ens()
 for i,u in pairs(py) do
  u.x=flr(rnd(2))
  u.y=i-1
  u.atb=0
  u.cd={0,0,0,0}
  u.buffs={}
  u.debuffs={}
  if u.hp>0 then u.alive=true end
 end
 cur={x=0,y=0}
 selu=1
end

function init_combat()
 gs="combat"
 cmsg=""
 cmt=0
 pts={}
 ftx={}
 cspd=1
 potmenu=false
end

-- particles + floating text
pts={}
ftx={}
function addp(gx,gy,col)
 for i=1,4 do
  add(pts,{
   x=gx*14+34+rnd(6),
   y=gy*14+24+rnd(6),
   dx=rnd(2)-1,dy=-rnd(1.5),
   l=12+rnd(8),c=col
  })
 end
end

function addfloat(gx,gy,txt,col)
 add(ftx,{
  x=gx*14+32,y=gy*14+18,
  txt=txt,c=col,l=30,dy=-0.4
 })
end

function uptp()
 for p in all(pts) do
  p.x+=p.dx
  p.y+=p.dy
  p.l-=1
  if p.l<=0 then del(pts,p) end
 end
 for f in all(ftx) do
  f.y+=f.dy
  f.l-=1
  if f.l<=0 then del(ftx,f) end
 end
end

-- accessory stat bonus for unit
function accb(u,stat)
 if not u.acc then return 0 end
 local a=_a[u.acc]
 if a[2]==sub(stat,1,1) then
  return n(a[3])
 end
 return 0
end

-- buff/debuff modifier for stat
function bufmod(u,st)
 local m=0
 for b in all(u.buffs) do
  if b.st==st then m+=b.val end
 end
 for d in all(u.debuffs) do
  if d.st==st then m-=d.val end
 end
 return m
end

-- compute buff/debuff value from skill
function bfval(u,tgt,s)
 local pw=n(s[4])
 local x=s[7]
 if x=="s" then return pw end
 if x=="a" then
  if pw<=5 then return pw end
  return max(1,flr(pw*tgt.atk/100))
 end
 if x=="d" then
  return max(1,flr(pw*tgt.def/100))
 end
 return pw
end

-- v2 damage calc: pw is x10 mult
function calcdmg(u,pw,tgt,pierce,slv)
 local ab=accb(u,"atk")+bufmod(u,"a")
 local d=flr(n(pw)*u.atk/10)+ab
 if slv and slv>1 then d=flr(d*(1+(slv-1)*0.2)) end
 if not pierce then
  d=d-(tgt.def+bufmod(tgt,"d"))
 end
 -- mark: +50% damage
 for db in all(tgt.debuffs) do
  if db.st=="m" then d=flr(d*1.5) break end
 end
 d+=flr(rnd(3))-1
 return max(1,d)
end

-- combat ai: 11 effect handlers
function doact(u)
 tickbd(u)
 -- stun check
 for d in all(u.debuffs) do
  if d.st=="n" then
   del(u.debuffs,d)
   cmsg=u.nm.." stunned"
   cmt=15 return
  end
 end

 local fr,fo={},{}
 for o in all(py) do
  if o.alive then
   if u.tm==1 then add(fr,o) else add(fo,o) end
  end
 end
 for o in all(ens) do
  if o.alive then
   if u.tm==2 then add(fr,o) else add(fo,o) end
  end
 end
 if #fo==0 then return end

 local sks
 if u.tm==1 then sks=ugetsk(u)
 else
  sks={}
  if u.ji>0 then
   for s in all(_s) do
    if n(s[2])==u.ji then add(sks,s) end
   end
  end
 end

 -- 1) heal check (h, H + revive)
 for i,s in pairs(sks) do
  if (s[3]=="h" or s[3]=="H") and u.cd[min(i,#u.cd)]==0 then
   if s[7]=="r" then
    -- revive: find dead ally
    local pool=u.tm==1 and py or ens
    for o in all(pool) do
     if not o.alive then
      o.alive=true
      o.hp=max(1,flr(o.mhp*n(s[4])/100))
      cmsg=s[1].." revive!"
      cmt=25 addp(o.x,o.y,11)
      u.cd[min(i,#u.cd)]=n(s[6])
      sfx(1) return
     end
    end
   end
   local tgt=nil
   for f in all(fr) do
    if f.hp<f.mhp*0.5 then
     if not tgt or f.hp<tgt.hp then tgt=f end
    end
   end
   if tgt or s[3]=="H" then
    local lm=u.slv and u.slv[min(i,3)] or 1
    local pw=flr(n(s[4])*u.atk/10*(1+(lm-1)*0.2))
    if s[3]=="H" then
     for f in all(fr) do f.hp=min(f.mhp,f.hp+pw) end
     cmsg=s[1].." +"..pw
    for f in all(fr) do addfloat(f.x,f.y,"+"..pw,11) end
    else
     tgt.hp=min(tgt.mhp,tgt.hp+pw)
     cmsg=s[1].." +"..pw
     addfloat(tgt.x,tgt.y,"+"..pw,11)
     addp(tgt.x,tgt.y,11)
    end
    cmt=25
    u.cd[min(i,#u.cd)]=n(s[6])
    sfx(1) return
   end
  end
 end

 -- 2) find target (taunt + behavior)
 local tgt,bd=nil,999
 local bf=u.bf or 0
 -- taunt override: target unit with taunt buff
 for f in all(fo) do
  for b in all(f.buffs) do
   if b.st=="t" then
    tgt=f bd=abs(f.x-u.x)+abs(f.y-u.y)
   end
  end
 end
 if not tgt then
  local pool=fo
  if bf==0 and u.tm==2 and #fo>1 then
   local mx=0
   for f in all(fo) do if f.x>mx then mx=f.x end end
   pool={}
   for f in all(fo) do if f.x==mx then add(pool,f) end end
  end
  for f in all(pool) do
   local d=abs(f.x-u.x)+abs(f.y-u.y)
   if bf==1 then
    if not tgt or f.hp<tgt.hp or(f.hp==tgt.hp and d<bd) then
     tgt=f bd=d
    end
   elseif bf==2 then
    if not tgt or f.x<tgt.x or(f.x==tgt.x and d<bd) then
     tgt=f bd=d
    end
   else
    if d<bd then tgt=f bd=d end
   end
  end
 end
 if tgt then bd=abs(tgt.x-u.x)+abs(tgt.y-u.y) end

 -- 3) debuff check (d, D)
 for i,s in pairs(sks) do
  local tp=s[3]
  if (tp=="d" or tp=="D") and u.cd[min(i,#u.cd)]==0 then
   local x=s[7]
   local dur=n(s[8])
   if tp=="D" then
    if x=="t" then
     -- taunt: buff self so enemies target us
     add(u.buffs,{st="t",val=0,dur=dur})
    else
     for f in all(fo) do
      add(f.debuffs,{st=x,val=bfval(u,f,s),dur=dur})
     end
    end
    cmsg=s[1].."!"
    cmt=20
    u.cd[min(i,#u.cd)]=n(s[6])
    addp(u.x,u.y,14) sfx(2) return
   elseif bd<=n(s[5]) and tgt then
    if x=="0" and n(s[4])==0 then
     -- steal: take a buff from target
     if #tgt.buffs>0 then
      local b=tgt.buffs[1]
      del(tgt.buffs,b)
      add(u.buffs,b)
      cmsg="stole buff!"
     end
    else
     add(tgt.debuffs,{st=x,val=bfval(u,tgt,s),dur=dur})
     cmsg=s[1].."!"
    end
    cmt=20
    u.cd[min(i,#u.cd)]=n(s[6])
    addp(tgt.x,tgt.y,14) sfx(2) return
   end
  end
 end

 -- 4) buff check (b, B, c)
 for i,s in pairs(sks) do
  local tp=s[3]
  if (tp=="b" or tp=="B" or tp=="c") and u.cd[min(i,#u.cd)]==0 then
   local x=s[7]
   local dur=n(s[8])
   if tp=="c" then
    add(u.buffs,{st="c",val=n(s[4]),dur=dur})
    cmsg=s[1].."!"
   elseif tp=="B" then
    for f in all(fr) do
     add(f.buffs,{st=x,val=bfval(u,f,s),dur=dur})
    end
    cmsg=s[1].." all!"
   else
    local btgt=u
    if n(s[5])>0 then
     for f in all(fr) do
      if f!=u and abs(f.x-u.x)+abs(f.y-u.y)<=n(s[5]) then
       btgt=f break
      end
     end
    end
    local val=bfval(u,btgt,s)
    add(btgt.buffs,{st=x,val=val,dur=dur})
    cmsg=s[1].." +"..val
   end
   cmt=20
   u.cd[min(i,#u.cd)]=n(s[6])
   addp(u.x,u.y,12) sfx(2) return
  end
 end

 -- 5) attack skills (a, A, p, l)
 for i,s in pairs(sks) do
  local tp=s[3]
  if (tp=="a" or tp=="A" or tp=="p" or tp=="l") and u.cd[min(i,#u.cd)]==0 then
   if tp=="A" then
    local dm=calcdmg(u,s[4],fo[1],false,u.slv and u.slv[min(i,3)])
    for f in all(fo) do
     f.hp-=dm f.flash=4
     if f.hp<=0 then f.alive=false f.dead_t=8 end
     addp(f.x,f.y,8)
     addfloat(f.x,f.y,"-"..dm,8)
    end
    cmsg=s[1].." -"..dm
    cmt=25
    u.cd[min(i,#u.cd)]=n(s[6])
    sfx(0) return
   elseif bd<=n(s[5]) then
    local dm=calcdmg(u,s[4],tgt,tp=="p",u.slv and u.slv[min(i,3)])
    -- counter check (melee only)
    local ctr=false
    if bd<=1 then
     for b in all(tgt.buffs) do
      if b.st=="c" then
       local ref=flr(dm*b.val/100)
       u.hp-=ref u.flash=4
       if u.hp<=0 then u.alive=false u.dead_t=8 end
       del(tgt.buffs,b)
       ctr=true
       cmsg="counter! -"..ref
       break
      end
     end
    end
    if not ctr then
     tgt.hp-=dm tgt.flash=4
     cmsg=s[1].." -"..dm
     addfloat(tgt.x,tgt.y,"-"..dm,8)
     -- xtra effects: secondary debuff
     local x=s[7]
     if x!="0" and n(s[8])>0 then
      add(tgt.debuffs,{st=x,val=bfval(u,tgt,s),dur=n(s[8])})
     end
     if x=="k" then u.hp=min(u.mhp,u.hp+dm) end
     if x=="n" then add(tgt.debuffs,{st="n",val=0,dur=1}) end
    end
    if tp=="l" and not ctr then
     u.hp=min(u.mhp,u.hp+flr(dm/2))
    end
    cmt=25
    u.cd[min(i,#u.cd)]=n(s[6])
    if not ctr then
     if tgt.hp<=0 then tgt.alive=false tgt.dead_t=8 sfx(3)
     else sfx(0) end
    end
    addp(tgt.x,tgt.y,8) return
   end
  end
 end

 -- 6) move or basic attack
 if bd>1 then
  local dx=tgt.x>u.x and 1 or (tgt.x<u.x and -1 or 0)
  local dy=tgt.y>u.y and 1 or (tgt.y<u.y and -1 or 0)
  if dx!=0 and isopen(u.x+dx,u.y,u) then u.x+=dx
  elseif dy!=0 and isopen(u.x,u.y+dy,u) then u.y+=dy end
 else
  local a=u.atk+accb(u,"atk")+bufmod(u,"a")
  local df=tgt.def+bufmod(tgt,"d")
  local dm=max(1,a-df+flr(rnd(3))-1)
  -- counter check
  local ctr=false
  for b in all(tgt.buffs) do
   if b.st=="c" then
    u.hp-=flr(dm*b.val/100) u.flash=4
    if u.hp<=0 then u.alive=false u.dead_t=8 end
    del(tgt.buffs,b)
    ctr=true cmsg="counter!"
    break
   end
  end
  if not ctr then
   tgt.hp-=dm tgt.flash=4 cmsg="atk -"..dm
   addfloat(tgt.x,tgt.y,"-"..dm,8)
   if tgt.hp<=0 then tgt.alive=false tgt.dead_t=8 sfx(3)
   else sfx(0) end
  end
  cmt=20
  addp(tgt.x,tgt.y,8)
 end
end

-- tick buff/debuff durations
function tickbd(u)
 for i=#u.buffs,1,-1 do
  local b=u.buffs[i]
  if b.dur>0 then
   b.dur-=1
   if b.dur<=0 then del(u.buffs,b) end
  end
 end
 for i=#u.debuffs,1,-1 do
  local d=u.debuffs[i]
  -- poison DoT
  if d.st=="p" then
   u.hp-=d.val
   if u.hp<=0 then u.alive=false u.dead_t=8 end
  end
  if d.dur>0 then
   d.dur-=1
   if d.dur<=0 then del(u.debuffs,d) end
  end
 end
end

function cwin()
 -- gold reward
 local gr=15+flr(rnd(11))
 local nd=0
 for u in all(py) do
  if not u.alive then nd+=1 end
 end
 if nd==0 then gr+=5 end
 gold+=gr
 gs="reward"
 cmt=45
 rws=nil rwdr=nil
 rwacc={} rwunit=0 rwbr=0 rwski=0
 if cnod.tp==2 then
  -- elite: choose advance or accessory
  cmsg="elite won! +"..gr.."g"
  rws="elite_pick"
  sel=1
  sfx(5)
 elseif cnod.tp==4 then
  cmsg="boss defeated! +"..gr.."g"
  sfx(4)
 else
  cmsg="victory! +"..gr.."g"
  -- potion drop chance: 30%
  if rnd(100)<30 and #pots<3 then
   rwdr=1+flr(rnd(#_p))
   add(pots,rwdr)
  end
  sfx(4)
 end
end

-- apply potion to target
function use_pot(pi,tgt)
 local p=_p[pi]
 local eff=p[2]
 local pw=n(p[3])
 if eff=="h" then
  tgt.hp=min(tgt.mhp,tgt.hp+pw)
  cmsg=tgt.nm.." +"..pw.."hp"
 elseif eff=="e" then
  for i=1,#tgt.cd do tgt.cd[i]=0 end
  cmsg=tgt.nm.." cds reset"
 elseif eff=="s" then
  add(tgt.buffs,{st="s",val=3,dur=5})
  cmsg=tgt.nm.." hasted"
 elseif eff=="d" then
  -- bomb: damage all enemies
  for e in all(ens) do
   if e.alive then
    local d=max(1,pw-n(e.def or 0))
    e.hp-=d e.flash=4
    if e.hp<=0 then e.alive=false e.dead_t=8 end
    addp(e.x,e.y,8)
   end
  end
  cmsg="bomb! "..pw.." dmg"
 elseif eff=="n" then
  -- smoke: buff all allies def
  for u in all(py) do
   if u.alive then
    add(u.buffs,{st="d",val=5,dur=3})
   end
  end
  cmsg="smoke screen!"
 elseif eff=="r" then
  -- revive: bring back dead unit
  if not tgt.alive then
   tgt.alive=true
   tgt.hp=flr(tgt.mhp*pw/100)
   cmsg=tgt.nm.." revived!"
  else
   cmsg="already alive"
   return false
  end
 elseif eff=="t" then
  -- shield: temp def buff
  add(tgt.buffs,{st="d",val=flr(pw/10),dur=4})
  cmsg=tgt.nm.." shielded"
 end
 cmt=30
 return true
end

-- update combat
function upcbt()
 -- speed toggle
 if btnp(0) and btnp(1) then cspd=cspd%3+1 end
 if cmt>0 then
  cmt-=1
  return
 end

 -- potion menu
 if potmenu then
  uppot()
  return
 end

 -- open potion menu with 🅾️
 if btnp(4) and #pots>0 then
  potmenu=true
  potsel=1
  pottgt=0
  return
 end

 local pa,ea=false,false
 for u in all(py) do if u.alive then pa=true end end
 for e in all(ens) do if e.alive then ea=true end end

 if not ea then cwin() return end
 if not pa then gs="gover" sfx(3) return end

 -- tick atb
 local au={}
 for u in all(py) do if u.alive then add(au,u) end end
 for e in all(ens) do if e.alive then add(au,e) end end

 for _=1,cspd do
  for u in all(au) do
   u.atb+=max(1,u.spd+accb(u,"spd")+bufmod(u,"s"))
   if u.atb>=100 then
    u.atb=-20
    doact(u)
    for i=1,#u.cd do
     if u.cd[i]>0 then u.cd[i]-=1 end
    end
    return
   end
  end
 end
end

-- potion menu update
function uppot()
 if pottgt==0 then
  -- selecting potion
  if btnp(2) then potsel=max(1,potsel-1) sfx(2) end
  if btnp(3) then potsel=min(#pots,potsel+1) sfx(2) end
  if btnp(5) then
   -- selected a potion, now pick target
   local p=_p[pots[potsel]]
   local eff=p[2]
   -- bomb/smoke are untargeted
   if eff=="d" or eff=="n" then
    if use_pot(pots[potsel],py[1]) then
     deli(pots,potsel)
    end
    potmenu=false
    sfx(1)
   else
    pottgt=1
    sfx(2)
   end
  end
  if btnp(4) then
   -- cancel
   potmenu=false
   sfx(3)
  end
 else
  -- selecting target
  if btnp(2) then pottgt=max(1,pottgt-1) sfx(2) end
  if btnp(3) then pottgt=min(3,pottgt+1) sfx(2) end
  if btnp(5) and pottgt<=#py then
   local tgt=py[pottgt]
   if use_pot(pots[potsel],tgt) then
    deli(pots,potsel)
   end
   potmenu=false
   sfx(1)
  end
  if btnp(4) then
   pottgt=0
   sfx(3)
  end
 end
end

-- reward screen
function upreward()
 if cmt>0 then cmt-=1 return end

 if not rws then
  -- transition to skill_up
  if btnp(5) then
   rws="skill_up" rwsu=1 sel=1
   -- find first alive unit
   while rwsu<=3 and not py[rwsu].alive do rwsu+=1 end
   if rwsu>3 then
    cnod.dn=true gs="map" sfx(2)
   else sfx(2) end
  end
 elseif rws=="skill_up" then
  local u=py[rwsu]
  local sks=ugetsk(u)
  if btnp(2) then sel=max(1,sel-1) sfx(2) end
  if btnp(3) then sel=min(#sks,sel+1) sfx(2) end
  if btnp(5) then
   u.slv[min(sel,3)]+=1
   sfx(1)
   -- next alive unit
   rwsu+=1
   while rwsu<=3 and not py[rwsu].alive do rwsu+=1 end
   sel=1
   if rwsu>3 then
    cnod.dn=true gs="map" sfx(2)
   end
  end
 elseif rws=="elite_pick" then
  -- choose: 1=advance 2=accessory
  if btnp(2) then sel=max(1,sel-1) sfx(2) end
  if btnp(3) then sel=min(2,sel+1) sfx(2) end
  if btnp(5) then
   if sel==1 then
    -- find advanceable units (tier 1)
    rwunits={}
    for i,u in pairs(py) do
     if u.alive and u.tier==1 then
      add(rwunits,i)
     end
    end
    if #rwunits>0 then
     rws="pick_unit"
     sel=1
    else
     -- no tier-1 units, skip to accessory
     rws="pick_acc"
     rwacc={1+flr(rnd(#_a)),
      1+flr(rnd(#_a))}
     sel=1
    end
   elseif sel==2 then
    rws="pick_acc"
    rwacc={1+flr(rnd(#_a)),
     1+flr(rnd(#_a))}
    -- ensure different
    while rwacc[2]==rwacc[1] do
     rwacc[2]=1+flr(rnd(#_a))
    end
    sel=1
   end
   sfx(2)
  end
 elseif rws=="pick_unit" then
  -- pick which unit to advance
  if btnp(2) then sel=max(1,sel-1) sfx(2) end
  if btnp(3) then sel=min(#rwunits,sel+1) sfx(2) end
  if btnp(5) then
   rwunit=rwunits[sel]
   local opts=advopt(py[rwunit].base)
   if #opts>=2 then
    rwbranch=opts
    rws="pick_branch"
    sel=1
    sfx(2)
   end
  end
 elseif rws=="pick_branch" then
  -- pick which branch
  if btnp(2) then sel=max(1,sel-1) sfx(2) end
  if btnp(3) then sel=min(#rwbranch,sel+1) sfx(2) end
  if btnp(5) then
   rwbr=rwbranch[sel]
   rws="pick_skill"
   sel=1
   sfx(2)
  end
 elseif rws=="pick_skill" then
  -- pick skill to keep from old class
  local sks=getsk(py[rwunit].ji)
  if btnp(2) then sel=max(1,sel-1) sfx(2) cfm=false end
  if btnp(3) then sel=min(#sks,sel+1) sfx(2) cfm=false end
  if cfm then
   if btnp(5) then
    cfm=false
    advu(py[rwunit],rwbr,sel)
    rws=nil
    sfx(5)
   elseif btnp(4) then cfm=false sfx(3) end
  elseif btnp(5) then cfm=true end
 elseif rws=="pick_acc" then
  -- pick 1 of 2 accessories
  if btnp(0) then sel=max(1,sel-1) sfx(2) end
  if btnp(1) then sel=min(2,sel+1) sfx(2) end
  if btnp(5) then
   local ai=rwacc[sel]
   -- assign to a unit: go to unit pick
   rwacc_chosen=ai
   rwunits={}
   for i,u in pairs(py) do
    if u.alive then add(rwunits,i) end
   end
   rws="assign_acc"
   sel=1
   sfx(2)
  end
 elseif rws=="assign_acc" then
  -- assign accessory to a unit
  if btnp(2) then sel=max(1,sel-1) sfx(2) cfm=false end
  if btnp(3) then sel=min(#rwunits,sel+1) sfx(2) cfm=false end
  if cfm then
   if btnp(5) then
    cfm=false
    py[rwunits[sel]].acc=rwacc_chosen
    rws=nil
    sfx(5)
   elseif btnp(4) then cfm=false sfx(3) end
  elseif btnp(5) then cfm=true end
 end

 -- when reward flow done, confirm exits
 if not rws and rws!=nil then
  -- already nil from above
 end
end

-- campfire
function init_camp()
 gs="camp"
 sel=1
 campsub=false
end

-- ===== main loops =====
function _update60()
 t+=1
 uptp()

 if gs=="title" then
  if btnp(5) then
   init_draft()
   sfx(2)
  end
 elseif gs=="draft" then
  updraft()
 elseif gs=="equip" then
  upequip()
 elseif gs=="map" then
  upmap()
 elseif gs=="setup" then
  upset()
 elseif gs=="combat" then
  upcbt()
 elseif gs=="reward" then
  upreward()
 elseif gs=="camp" then
  upcamp()
 elseif gs=="shop" then
  upshop()
 elseif gs=="shasgn" then
  upshasgn()
 elseif gs=="skview" then
  upskview()
 elseif gs=="boss_intro" then
  upboss()
 elseif gs=="gover" then
  if btnp(5) then _init() end
 elseif gs=="win" then
  if btnp(5) then _init() end
 end
end

function upmap()
 local opts={}
 if cnod then
  for nd in all(cnod.cn) do
   if not nd.dn then add(opts,nd) end
  end
 end
 if #opts==0 then
  if cnod.row>=5 then
   if fl>=mxfl then gs="win"
   else fl+=1 genmap() end
   return
  end
 end
 if btnp(0) then sel=max(1,sel-1) sfx(2) end
 if btnp(1) then sel=min(#opts,sel+1) sfx(2) end
 if btnp(5) and #opts>0 then
  cnod=opts[sel]
  sel=1
  sfx(2)
  if cnod.tp==3 then init_camp()
  elseif cnod.tp==5 then init_shop()
  elseif cnod.tp==4 then init_boss()
  else init_setup() end
 end
end

function upset()
 if btnp(0) then cur.x=max(0,cur.x-1) cfm=false end
 if btnp(1) then cur.x=min(2,cur.x+1) cfm=false end
 if btnp(2) then cur.y=max(0,cur.y-1) cfm=false end
 if btnp(3) then cur.y=min(3,cur.y+1) cfm=false end
 if btnp(4) then init_skview("setup") return end

 if cfm then
  if btnp(5) then
   cfm=false
   py[selu].x=cur.x
   py[selu].y=cur.y
   selu+=1
   sfx(2)
   if selu>3 then init_combat() end
  elseif btnp(4) then cfm=false sfx(3) end
 elseif btnp(5) then
  local occ=false
  for i=1,selu-1 do
   if py[i].x==cur.x and py[i].y==cur.y then occ=true end
  end
  if not occ then
   if selu==3 then
    cfm=true
   else
    py[selu].x=cur.x
    py[selu].y=cur.y
    selu+=1
    sfx(2)
   end
  else
   sfx(3)
  end
 end
end

function uptrain()
 if trnu>3 then
  cnod.dn=true cmt=30
  gs="reward" rws=nil rwdr=nil
  campsub=false cmsg="training done!" sfx(1)
  return
 end
 local u=py[trnu]
 local sks=ugetsk(u)
 if btnp(2) then sel=max(1,sel-1) sfx(2) end
 if btnp(3) then sel=min(#sks,sel+1) sfx(2) end
 if btnp(5) then
  u.slv[min(sel,3)]+=1
  trnu+=1 sel=1 sfx(1)
 end
 if btnp(4) then
  campsub=false sel=3 sfx(3)
 end
end

function upcamp()
 if campsub=="train" then
  uptrain() return
 elseif campsub then
  upforge() return
 end
 if btnp(4) then init_skview("camp") return end
 if btnp(2) then sel=max(1,sel-1) sfx(2) cfm=false end
 if btnp(3) then sel=min(3,sel+1) sfx(2) cfm=false end
 if cfm then
  if btnp(5) then
   cfm=false
   if sel==1 then
    for u in all(py) do u.hp=u.mhp end
    cnod.dn=true cmt=30
    gs="reward" rws=nil rwdr=nil
    cmsg="party healed!" sfx(1)
   elseif sel==2 then
    campsub=true frgfrom=0 frgto=0
    sel=1 sfx(2)
   elseif sel==3 then
    campsub="train" trnu=1 sel=1
    sfx(2)
   end
  elseif btnp(4) then cfm=false sfx(3) end
 elseif btnp(5) then cfm=true end
end

function upforge()
 if frgfrom==0 then
  -- pick source unit
  if btnp(2) then sel=max(1,sel-1) sfx(2) end
  if btnp(3) then sel=min(3,sel+1) sfx(2) end
  if btnp(5) then
   frgfrom=sel
   sel=1
   sfx(2)
  end
  if btnp(4) then
   campsub=false
   sel=2
   sfx(3)
  end
 elseif frgto==0 then
  -- pick target unit
  if btnp(2) then sel=max(1,sel-1) sfx(2) end
  if btnp(3) then sel=min(3,sel+1) sfx(2) end
  if cfm then
   if btnp(5) then
    cfm=false
    local a1=py[frgfrom].acc
    local a2=py[sel].acc
    py[frgfrom].acc=a2
    py[sel].acc=a1
    cnod.dn=true cmt=30
    gs="reward" rws=nil rwdr=nil
    campsub=false
    cmsg="accessories swapped!" sfx(1)
   elseif btnp(4) then cfm=false sfx(3) end
  elseif btnp(5) and sel!=frgfrom then
   cfm=true
  end
  if not cfm and btnp(4) then
   frgfrom=0 sel=1 sfx(3)
  end
 end
end

function init_shop()
 gs="shop"
 sel=1
 -- generate shop items
 shitm={}
 -- 2-4 potions for sale
 local np=2+flr(rnd(3))
 for i=1,np do
  local pi=1+flr(rnd(#_p))
  add(shitm,{tp="pot",id=pi,
   cost=n(_p[pi][4])})
 end
 -- 2 accessories
 local a1=1+flr(rnd(#_a))
 local a2=1+flr(rnd(#_a))
 while a2==a1 do a2=1+flr(rnd(#_a)) end
 add(shitm,{tp="acc",id=a1,
  cost=80+flr(rnd(41))})
 add(shitm,{tp="acc",id=a2,
  cost=80+flr(rnd(41))})
 -- heal all option
 add(shitm,{tp="heal",id=0,cost=25})
end

function upshop()
 if btnp(2) then sel=max(1,sel-1) sfx(2) cfm=false end
 if btnp(3) then sel=min(#shitm+1,sel+1) sfx(2) cfm=false end
 if cfm then
  if btnp(5) then
   cfm=false
   if sel>#shitm then
    cnod.dn=true gs="map" sfx(2) return
   end
   local it=shitm[sel]
   if gold>=it.cost then
    gold-=it.cost
    if it.tp=="pot" then
     if #pots<3 then add(pots,it.id) deli(shitm,sel) sfx(1)
     else sfx(3) end
    elseif it.tp=="acc" then
     shacc=it.id shsel=sel gs="shasgn" sel=1 sfx(2)
    elseif it.tp=="heal" then
     for u in all(py) do u.hp=u.mhp end
     deli(shitm,sel) sfx(1)
    end
   else sfx(3) end
  elseif btnp(4) then cfm=false sfx(3) end
 elseif btnp(5) then cfm=true
 elseif btnp(4) then
  cnod.dn=true gs="map" sfx(2)
 end
end

function upshasgn()
 if btnp(2) then sel=max(1,sel-1) sfx(2) end
 if btnp(3) then sel=min(3,sel+1) sfx(2) end
 if btnp(5) then
  py[sel].acc=shacc
  deli(shitm,shsel)
  gs="shop"
  sel=1
  sfx(1)
 end
 if btnp(4) then
  -- cancel: refund gold
  gold+=shitm[shsel].cost
  gs="shop"
  sel=shsel
  sfx(3)
 end
end

-- boss intro
function init_boss()
 gs="boss_intro"
 local bi=min(fl,#_b)
 bossdat=_b[bi]
 cmt=60
end

function upboss()
 if cmt>0 then cmt-=1 return end
 if btnp(5) then
  init_setup()
  sfx(2)
 end
end

function dboss()
 cls(0)
 -- dramatic backdrop
 for i=0,127,8 do
  line(0,i+t%8,127,i+t%8,2)
 end
 rectfill(16,20,112,108,0)
 rect(16,20,112,108,8)
 rect(17,21,111,107,2)

 -- boss sprite (scaled via 4 spr calls)
 local sx=48
 spr(n(bossdat[2]),sx,32)
 spr(n(bossdat[2]),sx+8,32)
 spr(n(bossdat[2]),sx,40)
 spr(n(bossdat[2]),sx+8,40)

 -- boss name
 print(bossdat[1],40,56,8)
 print("floor "..fl.." boss",36,68,7)

 -- stats preview
 print("hp: "..bossdat[3],40,80,6)
 print("atk: "..bossdat[4],40,88,6)

 if cmt<=0 then
  if t%40<25 then
   print("\x97 to battle",34,98,10)
  end
 end
end

-- skill viewer
function init_skview(retgs)
 skret=retgs
 gs="skview"
 skunit=1
 skscr=0
end

function upskview()
 if btnp(0) then skunit=max(1,skunit-1) skscr=0 sfx(2) end
 if btnp(1) then skunit=min(3,skunit+1) skscr=0 sfx(2) end
 if btnp(2) then skscr=max(0,skscr-1) sfx(2) end
 if btnp(3) then skscr+=1 sfx(2) end
 if btnp(4) or btnp(5) then
  gs=skret
  sfx(2)
 end
end

function dskview()
 cls(0)
 rectfill(0,0,127,9,1)
 print("skill viewer",28,2,7)

 -- unit tabs
 for i,u in pairs(py) do
  local bx=2+(i-1)*42
  local c=i==skunit and 10 or 6
  rectfill(bx,12,bx+38,22,0)
  rect(bx,12,bx+38,22,c)
  spr(u.ji,bx+2,14)
  print(u.nm,bx+12,14,c)
 end

 local u=py[skunit]
 local y=26
 -- class info
 print(u.nm.." - "..jn[u.ji],4,y,7)
 y+=8
 if u.tier==2 then
  print("tier 2 (from "..jn[u.base]..")",4,y,5)
 else
  print("tier 1 (base)",4,y,5)
 end
 y+=8
 print("hp:"..u.mhp.." at:"..u.atk
  .." df:"..u.def.." sp:"..u.spd,4,y,6)
 y+=10

 -- accessory
 if u.acc then
  print("acc: ".._a[u.acc][1],4,y,10)
 else
  print("acc: none",4,y,5)
 end
 y+=10

 -- skills
 print("skills:",4,y,7) y+=8
 local sks=ugetsk(u)
 local si=skscr
 for i,s in pairs(sks) do
  if i>si then
   local ji=n(s[2])
   local show=true
   -- tier 2 skill descriptions hidden
   -- if class not discovered
   if n(_j[ji][7])==2 and not isdisc(ji) then
    show=false
   end
   if show then
    local lv=u.slv and u.slv[min(i,3)] or 1
    print(s[1].." lv"..lv,8,y,11)
    local tp=s[3]
    local tpnm={a="atk",["A"]="aoe",
     h="heal",["H"]="aoeh",b="buff",
     ["B"]="buffa",d="debuf",["D"]="deba",
     p="pierc",l="drain",c="counter"}
    print((tpnm[tp] or tp).." pw:"
     ..s[4].." rng:"..s[5].." cd:"..s[6],
     8,y+7,5)
   else
    print("???",8,y,5)
    print("(undiscovered)",8,y+7,5)
   end
   y+=16
   if y>120 then break end
  end
 end

 rectfill(0,120,127,127,1)
 print("\x8b\x91unit \x8e\x83scroll \x96back",4,122,5)
end

-- ===== drawing =====
function _draw()
 cls(0)
 if gs=="title" then dtitle()
 elseif gs=="draft" then ddraft()
 elseif gs=="equip" then dequip()
 elseif gs=="map" then dmap()
 elseif gs=="setup" then dsetup()
 elseif gs=="combat" then dcombat()
 elseif gs=="reward" then
  dreward()
 elseif gs=="camp" then dcamp()
 elseif gs=="shop" then dshop()
 elseif gs=="shasgn" then dshasgn()
 elseif gs=="skview" then dskview()
 elseif gs=="boss_intro" then dboss()
 elseif gs=="gover" then
  rectfill(12,16,116,112,0)
  rect(12,16,116,112,8)
  rect(13,17,115,111,2)
  print("game over",40,20,8)
  print("floor "..fl.."/"..mxfl,40,32,7)
  print("gold: "..gold,40,40,10)
  -- party fate
  for i,u in pairs(py) do
   local y=50+i*12
   spr(u.ji,18,y)
   print(u.nm.." "..jn[u.ji],30,y,
    u.alive and 6 or 8)
   if not u.alive then
    print("fallen",90,y,8)
   end
  end
  print("\x97 restart",38,100,6)
 elseif gs=="win" then
  rectfill(12,12,116,116,0)
  rect(12,12,116,116,11)
  rect(13,13,115,115,3)
  print("victory!",40,18,11)
  print("the spire is conquered!",14,28,7)
  print("gold: "..gold,40,38,10)
  -- party glory
  for i,u in pairs(py) do
   local y=46+i*14
   spr(u.ji,18,y)
   print(u.nm.." "..jn[u.ji],30,y,7)
   if u.tier==2 then
    print("t2",90,y,11)
   end
   if u.acc then
    print(_a[u.acc][1],90,y+7,5)
   end
  end
  print("\x97 new run",38,106,6)
 end
end

function dreward()
 dcombat()
 rectfill(4,30,124,124,0)
 rect(4,30,124,124,6)

 print(cmsg,8,33,7)
 print("gold:"..gold,8,41,10)

 if cmt>0 then return end

 if not rws then
  -- normal: show drop + confirm
  if rwdr then
   print("found: ".._p[rwdr][1],8,53,11)
  end
  print("\x97 level up skills",28,116,6)

 elseif rws=="skill_up" then
  local u=py[rwsu]
  print("train "..u.nm,8,53,11)
  print("pick a skill to level up:",8,63,7)
  local sks=ugetsk(u)
  for i,s in pairs(sks) do
   local c=i==sel and 10 or 6
   local lv=u.slv[min(i,3)]
   local y=74+(i-1)*14
   print(s[1].." lv"..lv,14,y,c)
   print("pw:"..s[4].." cd:"..s[6],14,y+7,5)
  end

 elseif rws=="elite_pick" then
  print("choose reward:",8,55,7)
  local c1=sel==1 and 10 or 6
  local c2=sel==2 and 10 or 6
  rectfill(10,65,60,85,0)
  rect(10,65,60,85,c1)
  print("advance",16,70,c1)
  print("unit",22,78,5)
  rectfill(68,65,118,85,0)
  rect(68,65,118,85,c2)
  print("pick",82,70,c2)
  print("accessory",72,78,5)

 elseif rws=="pick_unit" then
  print("advance which unit?",8,55,7)
  for i,ui in pairs(rwunits) do
   local u=py[ui]
   local c=i==sel and 10 or 6
   local y=62+(i-1)*14
   print(u.nm.." "..jn[u.ji],14,y,c)
   print("hp:"..u.mhp.." at:"..u.atk,14,y+7,5)
  end

 elseif rws=="pick_branch" then
  print("pick class branch:",8,55,7)
  for i,bi in pairs(rwbranch) do
   local j=_j[bi]
   local c=i==sel and 10 or 6
   local y=65+(i-1)*24
   rectfill(10,y,118,y+20,0)
   rect(10,y,118,y+20,c)
   spr(bi,14,y+2)
   print(jn[bi],26,y+2,c)
   print("hp:"..n(j[2]).." at:"..n(j[3])
    .." df:"..n(j[4]).." sp:"..n(j[5]),
    14,y+12,5)
  end

 elseif rws=="pick_skill" then
  print("keep which skill?",8,55,7)
  local sks=getsk(py[rwunit].ji)
  for i,s in pairs(sks) do
   local c=i==sel and 10 or 6
   local y=65+(i-1)*14
   print(s[1],14,y,c)
   print("pw:"..s[4].." rng:"..s[5]
    .." cd:"..s[6],14,y+7,5)
  end

 elseif rws=="pick_acc" then
  print("pick an accessory:",8,55,7)
  for i,ai in pairs(rwacc) do
   local a=_a[ai]
   local c=i==sel and 10 or 6
   local x=10+(i-1)*58
   rectfill(x,65,x+52,90,0)
   rect(x,65,x+52,90,c)
   print(a[1],x+4,68,c)
   if a[2]!="0" then
    print("+"..a[3].." "..a[2],x+4,78,5)
   else
    print("special:"..a[4],x+4,78,5)
   end
  end

 elseif rws=="assign_acc" then
  print("give to whom?",8,55,7)
  print(_a[rwacc_chosen][1],8,63,10)
  for i,ui in pairs(rwunits) do
   local u=py[ui]
   local c=i==sel and 10 or 6
   local y=72+(i-1)*14
   print(u.nm.." "..jn[u.ji],14,y,c)
   local cur_a="none"
   if u.acc then cur_a=_a[u.acc][1] end
   print("acc: "..cur_a,14,y+7,5)
  end
 end
 dcfm()
end

function dtitle()
 -- bg
 for i=0,15 do
  line(0,i*9+t%9,128,i*9+t%9,1)
 end
 rectfill(12,18,116,48,0)
 rect(12,18,116,48,6)
 print("spire tactics",24,24,7)
 print("roguelike auto-battler",14,34,5)
 -- class preview (6 base classes)
 for i=1,6 do
  spr(i,4+(i-1)*20,60)
  print(jn[i],1+(i-1)*20,70,6)
 end
 if t%50<35 then
  print("\x97 to begin",36,100,10)
 end
 print("x] start run",30,120,5)
end

function ddraft()
 cls(0)
 rectfill(0,0,127,9,1)
 print("choose your party",16,2,7)
 print(#dpick.."/3",108,2,10)

 -- role hints
 local roles={"front","back",
  "healer","mage","tank","mid"}

 for i=1,#dpool do
  local ji=dpool[i]
  local j=_j[ji]
  local x=2+(i-1)*25
  local y=14
  local pkd=_has(dpick,ji)
  local c=pkd and 5
   or (i==sel and 10 or 6)

  -- card bg
  rectfill(x,y,x+23,y+72,0)
  rect(x,y,x+23,y+72,c)

  -- sprite
  spr(ji,x+8,y+3)
  -- name
  print(jn[ji],x+2,y+13,c)
  -- role
  print(roles[ji],x+2,y+20,5)
  -- stats
  print("hp"..n(j[2]),x+2,y+30,7)
  print("at"..n(j[3]),x+2,y+38,8)
  print("df"..n(j[4]),x+2,y+46,12)
  print("sp"..n(j[5]),x+2,y+54,11)

  -- picked marker
  if pkd then
   rectfill(x+6,y+62,x+17,y+69,0)
   print("pick",x+4,y+63,11)
  end

  -- cursor
  if i==sel and not pkd then
   if t%30<20 then
    rect(x-1,y-1,x+24,y+73,10)
   end
  end
 end

 -- picked party preview
 rectfill(0,90,127,127,1)
 print("party:",2,92,6)
 for i,u in pairs(py) do
  local bx=4+(i-1)*42
  spr(u.ji,bx,100)
  print(u.nm,bx+10,100,7)
  print(jn[u.ji],bx+10,107,6)
 end

 if #dpick<3 then
  print("\x8b\x91 browse  \x97 pick",14,120,5)
 end
 dcfm()
end

function dmap()
 rectfill(0,0,127,7,1)
 print("floor "..fl.."/"..mxfl,2,1,7)
 print("g:"..gold,80,1,10)

 -- connections
 for nd in all(nds) do
  for c in all(nd.cn) do
   local col=5
   if nd==cnod then col=6 end
   line(nd.x+3,nd.y+3,c.x+3,c.y+3,col)
  end
 end

 -- nodes
 local opts={}
 if cnod then
  for c in all(cnod.cn) do
   if not c.dn then add(opts,c) end
  end
 end

 for nd in all(nds) do
  local sp=16
  if nd.tp>=1 and nd.tp<=5 then sp=15+nd.tp end
  if nd.tp==0 then sp=16 end

  local col=5
  if nd==cnod then
   col=7
   rect(nd.x-2,nd.y-2,nd.x+9,nd.y+9,7)
  elseif nd.dn then
   col=5
  end

  for i,o in pairs(opts) do
   if o==nd then
    if i==sel then
     col=10
     local blink=t%30<20
     if blink then
      rect(nd.x-2,nd.y-2,nd.x+9,nd.y+9,10)
     end
    else
     col=6
    end
   end
  end

  spr(sp,nd.x,nd.y)
 end

 -- selected node preview
 if #opts>0 and sel<=#opts then
  local sn=opts[sel]
  local nms={"battle","elite","campfire","boss","shop"}
  local cols={6,9,11,8,10}
  local tp=sn.tp
  if tp>=1 and tp<=5 then
   rectfill(0,90,127,98,1)
   print("\x83:"..nms[tp],4,92,cols[tp])
  end
 end

 -- party bar
 rectfill(0,100,127,127,1)
 for i,u in pairs(py) do
  local bx=1+(i-1)*43
  spr(u.ji,bx,101)
  print(u.nm,bx+10,101,7)
  print(jn[u.ji],bx+10,108,6)
  local hw=flr(30*u.hp/u.mhp)
  rectfill(bx,117,bx+30,120,5)
  rectfill(bx,117,bx+hw,120,u.hp>u.mhp*0.3 and 11 or 8)
  print(u.hp.."/"..u.mhp,bx,122,7)
 end
end

function dsetup()
 rectfill(0,0,127,9,1)
 print("place unit "..selu.."/3",4,2,7)
 -- enemy count
 local tp=cnod.tp
 local lbl=tp==4 and "boss" or
  (tp==2 and "elite" or "battle")
 print(lbl.." x"..#ens,80,2,
  tp==4 and 8 or (tp==2 and 9 or 6))

 -- grid 6x4 with side tinting
 local gx0,gy0=22,14
 local cs=14
 for gx=0,5 do
  for gy=0,3 do
   local bx=gx0+gx*cs
   local by=gy0+gy*cs
   local c
   if gx<=2 then c=(gx+gy)%2==0 and 3 or 1
   else c=(gx+gy)%2==0 and 2 or 1 end
   rectfill(bx,by,bx+cs-2,by+cs-2,c)
  end
 end
 line(gx0+3*cs-1,gy0,gx0+3*cs-1,gy0+4*cs-2,5)

 -- enemy preview on grid
 for e in all(ens) do
  local bx=gx0+e.x*cs+3
  local by=gy0+e.y*cs+3
  spr(e.spr,bx,by)
 end

 -- placed units
 for i=1,min(selu-1,3) do
  local u=py[i]
  local bx=gx0+u.x*cs+3
  local by=gy0+u.y*cs+3
  spr(u.ji,bx,by)
 end

 -- cursor
 local cx=gx0+cur.x*cs-1
 local cy=gy0+cur.y*cs-1
 rect(cx,cy,cx+cs,cy+cs,10)

 -- bottom panel
 rectfill(0,72,127,127,1)
 rect(0,72,127,127,6)

 -- current unit info
 local u=py[min(selu,3)]
 spr(u.ji,4,74)
 print(u.nm.." "..jn[u.ji],14,74,7)
 print("hp:"..u.mhp.." at:"..u.atk
  .." df:"..u.def.." sp:"..u.spd,4,83,6)
 -- skills with readable types
 local tpnm={a="ATK",A="AOE",h="HEAL",H="HAOE",b="BUFF",B="BFALL",d="DEBF",D="DBALL",p="PIERC",l="DRAIN",c="CNTR"}
 local sks=ugetsk(u)
 local sx=4
 for si=1,min(#sks,3) do
  local s=sks[si]
  local tn=tpnm[s[3]] or s[3]
  local lv=u.slv and u.slv[min(si,3)] or 1
  print(s[1].." "..tn.." lv"..lv,sx,91,12)
  sx+=42
 end

 -- enemy lineup
 print("enemies:",4,99,8)
 local ex=4
 for e in all(ens) do
  spr(e.spr,ex,107)
  print(e.nm,ex+10,107,6)
  print("hp:"..e.mhp.." at:"..e.atk,
   ex+10,114,5)
  ex+=42
 end

 print("\x97=place  \x96=skills",4,122,5)
 dcfm()
end

function dcombat()
 -- grid with side tinting
 local gx0,gy0=22,14
 local cs=14
 for gx=0,5 do
  for gy=0,3 do
   local bx=gx0+gx*cs
   local by=gy0+gy*cs
   local c
   if gx<=2 then c=(gx+gy)%2==0 and 3 or 1
   else c=(gx+gy)%2==0 and 2 or 1 end
   rectfill(bx,by,bx+cs-2,by+cs-2,c)
  end
 end
 line(gx0+3*cs-1,gy0,gx0+3*cs-1,gy0+4*cs-2,5)

 -- draw party units (green)
 for u in all(py) do
  if u.alive then
   local bx=gx0+u.x*cs+3
   local by=gy0+u.y*cs+3
   rect(bx-1,by-1,bx+8,by+8,11)
   if u.flash and u.flash>0 then
    rectfill(bx,by,bx+7,by+7,7)
    u.flash-=1
   else
    spr(u.ji,bx,by)
   end
   local hw=flr(8*u.hp/u.mhp)
   rectfill(bx,by+9,bx+8,by+10,5)
   rectfill(bx,by+9,bx+hw,by+10,11)
   local aw=flr(8*max(0,u.atb)/100)
   rectfill(bx,by+11,bx+8,by+11,1)
   rectfill(bx,by+11,bx+aw,by+11,10)
   if #u.buffs>0 then print(#u.buffs,bx,by-5,11) end
   if #u.debuffs>0 then print(#u.debuffs,bx+5,by-5,8) end
   print(sub(u.nm,1,3),bx,by+13,11)
  end
 end
 -- draw enemies (red)
 for e in all(ens) do
  if e.alive then
   local bx=gx0+e.x*cs+3
   local by=gy0+e.y*cs+3
   rect(bx-1,by-1,bx+8,by+8,8)
   if e.flash and e.flash>0 then
    rectfill(bx,by,bx+7,by+7,7)
    e.flash-=1
   else
    spr(e.spr,bx,by)
   end
   local hw=flr(8*e.hp/e.mhp)
   rectfill(bx,by+9,bx+8,by+10,5)
   rectfill(bx,by+9,bx+hw,by+10,8)
   local aw=flr(8*max(0,e.atb)/100)
   rectfill(bx,by+11,bx+8,by+11,1)
   rectfill(bx,by+11,bx+aw,by+11,10)
   if #e.buffs>0 then print(#e.buffs,bx,by-5,11) end
   if #e.debuffs>0 then print(#e.debuffs,bx+5,by-5,8) end
  end
 end

 -- death poof
 for u in all(py) do
  if u.dead_t and u.dead_t>0 then
   local bx=gx0+u.x*cs+3
   local by=gy0+u.y*cs+3
   for i=0,7 do pset(bx+rnd(8),by+rnd(8),rnd(1)<.5 and 7 or 6) end
   u.dead_t-=1
  end
 end
 for e in all(ens) do
  if e.dead_t and e.dead_t>0 then
   local bx=gx0+e.x*cs+3
   local by=gy0+e.y*cs+3
   for i=0,7 do pset(bx+rnd(8),by+rnd(8),rnd(1)<.5 and 7 or 6) end
   e.dead_t-=1
  end
 end

 -- particles
 for p in all(pts) do
  pset(p.x,p.y,p.c)
 end

 -- floating text
 for f in all(ftx) do
  if f.l>10 then
   print(f.txt,f.x,f.y,f.c)
  elseif f.l>0 and f.l%2==0 then
   print(f.txt,f.x,f.y,f.c)
  end
 end

 -- top hud
 rectfill(0,0,127,11,1)
 if cmt>0 then
  print(cmsg,4,2,7)
 else
  print("floor "..fl,4,2,6)
 end
 print("g:"..gold,100,2,10)

 -- bottom panel: party + cooldowns
 rectfill(0,82,127,127,1)
 line(0,82,127,82,6)
 for i,u in pairs(py) do
  local bx=(i-1)*43
  local by=84
  spr(u.ji,bx+1,by)
  print(u.nm,bx+10,by,u.alive and 7 or 5)
  local hw=flr(20*u.hp/u.mhp)
  rectfill(bx+10,by+7,bx+30,by+9,5)
  rectfill(bx+10,by+7,bx+10+hw,by+9,u.hp>u.mhp*0.3 and 11 or 8)
  if u.alive then
   local sks=ugetsk(u)
   for si=1,min(#sks,3) do
    local cd=u.cd[si] or 0
    local cx=bx+32+(si-1)*4
    if cd==0 then
     rectfill(cx,by+7,cx+2,by+9,11)
    else
     rectfill(cx,by+7,cx+2,by+9,8)
    end
   end
  end
 end
 -- enemy summary row
 local ei=0
 for e in all(ens) do
  if e.alive then
   local bx=ei*32
   local by=96
   spr(e.spr,bx+1,by)
   print(sub(e.nm,1,4),bx+10,by,7)
   local hw=flr(16*e.hp/e.mhp)
   rectfill(bx+10,by+7,bx+26,by+9,5)
   rectfill(bx+10,by+7,bx+10+hw,by+9,8)
   ei+=1
  end
 end
 -- action log
 if cmt>0 then
  rectfill(0,108,127,116,0)
  print(cmsg,2,110,7)
 end
 -- speed + potion indicator
 print("x"..cspd,118,122,5)
 if #pots>0 and not potmenu and cmt<=0 then
  if t%40<25 then
   print("\x96"..#pots,100,122,11)
  end
 end

 -- potion overlay
 if potmenu then
  rectfill(2,20,126,90,0)
  rect(2,20,126,90,11)
  print("potions",4,22,11)

  if pottgt==0 then
   for i,pi in pairs(pots) do
    local p=_p[pi]
    local c=i==potsel and 10 or 6
    local y=30+(i-1)*16
    print(p[1],8,y,c)
    print("eff:"..p[2].." pw:"..p[3],8,y+7,5)
   end
   print("\x96 cancel  \x97 use",8,82,5)
  else
   print("use ".._p[pots[potsel]][1].." on:",8,30,11)
   for i,u in pairs(py) do
    local c=i==pottgt and 10 or 6
    local y=40+(i-1)*14
    print(u.nm.." "..jn[u.ji],12,y,c)
    local st=u.alive and
     (u.hp.."/"..u.mhp.."hp") or "dead"
    print(st,12,y+7,u.alive and 5 or 8)
   end
   print("\x96 back  \x97 use",8,82,5)
  end
 end
end

function dcamp()
 rectfill(10,10,118,118,0)
 rect(10,10,118,118,9)
 rect(11,11,117,117,4)
 spr(18,52,16)
 print("campfire",40,26,9)

 if not campsub then
  print("choose one:",34,38,7)
  for i,u in pairs(py) do
   print(u.nm.." "..jn[u.ji]..": "
    ..u.hp.."/"..u.mhp,24,48+i*10,6)
  end
  local opts={"rest (heal all)",
   "reforge (swap acc)","train (level skill)"}
  for i=1,3 do
   local c=i==sel and 10 or 6
   print(opts[i],20,80+i*10,c)
   if i==sel then print(">",14,80+i*10,10) end
  end
  print("\x97 to select",36,116,5)
 elseif campsub=="train" then
  if trnu<=3 then
   local u=py[trnu]
   print("train "..u.nm,34,38,11)
   local sks=ugetsk(u)
   for i,s in pairs(sks) do
    local c=i==sel and 10 or 6
    local lv=u.slv[min(i,3)]
    local y=50+(i-1)*16
    print(s[1].." lv"..lv,18,y,c)
    print("pw:"..s[4].." cd:"..s[6],18,y+7,5)
    if i==sel then print(">",12,y,10) end
   end
  end
  print("\x96 cancel  \x97 pick",20,116,5)
 else
  -- reforge sub-menu
  if frgfrom==0 then
   print("swap from:",34,38,7)
  else
   print("swap to:",34,38,7)
  end
  for i,u in pairs(py) do
   local c=i==sel and 10 or 6
   local y=48+i*14
   spr(u.ji,18,y)
   print(u.nm,28,y,c)
   local anm="none"
   if u.acc then anm=_a[u.acc][1] end
   print("acc:"..anm,28,y+7,5)
   if i==sel then print(">",12,y,10) end
  end
  print("\x96 cancel  \x97 pick",20,116,5)
 end
 dcfm()
end

function dshop()
 rectfill(4,4,124,124,0)
 rect(4,4,124,124,10)
 rect(5,5,123,123,4)
 spr(20,48,8)
 print("shop",56,10,10)
 print("gold:"..gold,80,10,10)

 for i,it in pairs(shitm) do
  local c=i==sel and 10 or 6
  local y=22+(i-1)*14
  if it.tp=="pot" then
   print(_p[it.id][1],12,y,c)
   print("potion",60,y,5)
  elseif it.tp=="acc" then
   print(_a[it.id][1],12,y,c)
   if _a[it.id][2]!="0" then
    print("+"..n(_a[it.id][3]).." "
     .._a[it.id][2],60,y,5)
   else
    print("spc:"
     .._a[it.id][4],60,y,5)
   end
  elseif it.tp=="heal" then
   print("heal all",12,y,c)
   print("restore hp",60,y,5)
  end
  print(it.cost.."g",104,y,
   gold>=it.cost and 10 or 8)
  if i==sel then print(">",6,y,10) end
 end

 -- leave option
 local ly=22+#shitm*14
 local c=sel>#shitm and 10 or 6
 print("leave shop",12,ly,c)
 if sel>#shitm then print(">",6,ly,10) end

 -- potions carried
 rectfill(4,108,124,122,1)
 print("pots:"..#pots.."/3",8,110,6)
 for i,pi in pairs(pots) do
  print(_p[pi][1],40+(i-1)*30,110,5)
 end
 print("\x96 leave  \x97 buy",8,118,5)
 dcfm()
end

function dshasgn()
 rectfill(10,20,118,108,0)
 rect(10,20,118,108,10)
 print("give ".._a[shacc][1].." to:",14,24,10)
 for i,u in pairs(py) do
  local c=i==sel and 10 or 6
  local y=36+(i-1)*18
  spr(u.ji,14,y)
  print(u.nm.." "..jn[u.ji],26,y,c)
  local cur_a="none"
  if u.acc then cur_a=_a[u.acc][1] end
  print("acc: "..cur_a,26,y+8,5)
  if i==sel then print(">",8,y,10) end
 end
 print("\x96 cancel  \x97 equip",14,96,5)
end
__gfx__
0000000000fff00000666000000e000000fff0000000000000888000000000000494490080008000000000600000000000000000000000000006600000777000
0000000000f7f0000667660000eee00000f7f00000bbb0000880880055500000499999408808880000000600088088000cccccc0000a00000006600007777700
0000000000fff0000066600000fff000007770000bbbbb000088800055555000490709400888880000006000888888800cc77cc000aaa0000066600007070700
000000000044400000ccc0000022200000bbb000bb7b7bb00088800057555500499999408e888e8000060000888888800c7777c00aa0aa0006bbb60007777700
000000000944409006ccc0600222220003bbb030bbbbbbb00888880055555550049994000888880004060000088888000cc77cc000aaa0000bbbbb0000777000
000000000044400000ccc0000022200000b3b0000bbbbb0000888000055555004949494008888000004000000088800000cccc00000a00000bbbbb0000777000
000000000004040000c0c0000002020000b0b00000bbb0000080800005005000040904000a080a000400000000080000000cc0000000000006bbb60007070700
000000000004040000c0c0000002020000b0b0000000000000800800050050000409040008000800000000000000000000000000000000000066600000000000
6000000600aaa000000900000a000a0000aaaa000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
060000600a777a00009900000a0a0a000aaaaaa000000000000c0000000000000000000000000000000000000000000000000000000000000000000000000000
006006000777770009a990000aaaaa000aa99aa000aaaa0000ccc000000000000000000000000000000000000000000000000000000000000000000000000000
000660000708070009aa90000aaaaa000a9aa9a00aaaaaa00cc7cc00000000000000000000000000000000000000000000000000000000000000000000000000
00066000077777009aaaa900099999000a9aa9a00aaaaaa000ccc000000000000000000000000000000000000000000000000000000000000000000000000000
00600600007770000aaaa000099999000aa99aa000aaaa00000c0000000000000000000000000000000000000000000000000000000000000000000000000000
060000600707070004444400099999000aaaaaa00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
6000000600000000004440000000000000aaaa000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00090000000c0000055555000044000000000000033330000000000000999000000200000003c00004444000800000800888800030030030002c200000000000
0099000000ccc000557555000484000020000020337330000003300009a9900000222000003330004474400088000880898980003303303302c2c20000000000
09a990000c0c0c005555550004444000220002203333300000383000999999000202020003030300444440000888880088888800033333002c222c0000000000
09999f0000ccc0005575550000484000022222003373300003330000099990000022200000333000444440000887880089898000033333000222200000000000
00999000000c000055555500004440000227720033333000333000000999900000020000000300004474400088888880888880003333333002c2200000000000
0099000000ccc0000555500000440000022222000333300033380000009990000022200000333000044440000888880008888000033333000022200000000000
090090000c000c000550550004004000002220000303030003330000090090000200020003000300040404000088800008080800003330000200020000000000
090090000c000c000500500004004000000200000300300000330000090090000200020003000300040040000080800008008000003030000200020000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
__gff__
0000000000000000000000000000000000000000000000000000000000000000010100000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
__map__
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
__sfx__
0104000024665206551c6451863514625106150000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
01080000180301b0401e0502106024070270702a0702d070000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
010400002035022350243502635000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
011000002456522565205551e5551c5451a54518535165351452512525105150e5150000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
01100000180601c0601f06024060240601f0602406027060000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
0106000024356283562c35624356283562c35624356283162c3162431600000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000
__music__
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141
00 41414141