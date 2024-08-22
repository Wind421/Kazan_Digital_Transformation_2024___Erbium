import database_telegrambot as bd

from aiogram import Router, F
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from aiogram.types import Message,InlineKeyboardButton,ContentType,KeyboardButton,\
    ReplyKeyboardRemove,ReplyKeyboardMarkup,InlineKeyboardMarkup,CallbackQuery,FSInputFile
from aiogram.filters import CommandStart,Command
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext


TOKEN = '7421909036:AAENAJ-e0r57xriyNWi1EPorsZGBd_NQUgE'
dp = Dispatcher()
bot = Bot(token=TOKEN, default=DefaultBotProperties())
router = Router()

class IdeaViewing(StatesGroup):
    offset = State()
    viewing = State()
class IdeaForm(StatesGroup):
    title = State()
    text = State()
    address = State()
    photo = State()
class Form(StatesGroup):
    action = State()
class ChangeIdeaState(StatesGroup):
    title = State()
    text = State()
    adress = State()
    photo = State()

spravka = "Чтобы перейти в меню, нажмите /menu\nЧтобы посмотреть профиль /profile"
@dp.message(CommandStart())
async def start_def(message: Message):
    await message.reply(
        f'''Привет, {message.from_user.first_name}! 🌟
Добро пожаловать в бота "Действуй, город!" – вашего помощника в мире инициатив и голосований.
Здесь ты можешь поделиться своими идеями, которые могут помочь улучшить наш город :)''',parse_mode=ParseMode.MARKDOWN 
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [
        InlineKeyboardButton(text='Конечно хочу!', callback_data="now_post"),
        InlineKeyboardButton(text='В следующий раз...', callback_data="other_day"),
    ]])

    await bot.send_message(message.chat.id,
                           'Если ты хочешь подробнее рассказать о своих идеях, оставь свой номер и тебе обязательно позвонят :)',
                           reply_markup=markup)  

#region    
@dp.callback_query(lambda call: call.data.startswith('now_'))
async def callback_create(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    await state.update_data(action=callback_query.data)

    contact_button = KeyboardButton(text='Отправить мой номер телефона', request_contact=True)
    contact_keyboard = ReplyKeyboardMarkup(keyboard=[[contact_button]],
                                           resize_keyboard=True, 
                                           one_time_keyboard=True)

    await bot.send_message(callback_query.from_user.id,
                           'Нажмите на кнопку ниже, чтобы отправить ваш номер телефона:',
                           reply_markup=contact_keyboard)
    
@dp.message(F.contact)
async def contact_handler(message: Message, state: FSMContext):
    data = await state.get_data()
    action = data.get('action')
    
    if action == "now_post":

        user_id = message.from_user.id
        first_name = message.from_user.first_name
        last_name = message.from_user.last_name
        phone_number = message.contact.phone_number

        bd.post_user(user_id, first_name, last_name, phone_number)
        await message.answer(
            '''Ваш номер телефона был успешно получен!\n'''+spravka,
            reply_markup=ReplyKeyboardRemove()
        )

    elif action == "now_change":
        user_id = message.from_user.id
        phone_number = message.contact.phone_number 

        bd.set_user(user_id, phone_number)
        await message.answer('Ваш номер успешно изменен!\n'+spravka,
                             reply_markup=ReplyKeyboardRemove())
        
    await state.clear()
    
    
@dp.callback_query(lambda call: call.data == 'other_day')
async def callback_create(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    bd.post_user(callback_query.from_user.id, 
                callback_query.from_user.first_name, 
                callback_query.from_user.last_name)
    await bot.send_message(callback_query.message.chat.id, spravka)
#endregion

@dp.message(Command(commands=['help']))
async def help_def(message: Message):
    await bot.send_message(chat_id=message.chat.id, 
                    text=clean_message('''
                    <b>Справка</b>
                    /menu - главное меню
                    /profile - просмотр профиля пользователя
                    /help - вызов справки
                    /start - приветственное сообщение
                    '''), 
                    parse_mode=ParseMode.HTML)
    
@dp.message(Command(commands=['profile']))
async def profile_def(message: Message):
    data = bd.get_profile(message.from_user.id)
    if data['phone']==None:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить телефон', callback_data='now_change'),
                InlineKeyboardButton(text='Изменить район', callback_data='region')
            ],
            [InlineKeyboardButton(text='Все отлично!', callback_data='ideafix_Все отлично!_None_None')]
        ])
    else:
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Изменить район', callback_data='region')],
            [InlineKeyboardButton(text='Все отлично!', callback_data='ideafix_Все отлично!_None_None')]
        ])
    await bot.send_message(chat_id=message.chat.id,
                           text=clean_message(f'''
                            Твой текущий профиль:\n
                            Имя: {data['first_name']}
                            Фамилия: {data['last_name']}
                            Телефон: {data['phone']}
                            Интересующий район: {data['region']}
                            '''),
                            reply_markup=markup)

@dp.message(Command(commands=['menu']))
async def menu_def(message: Message):

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отправить\nинициативу', callback_data="create")],
        [InlineKeyboardButton(text='Посмотреть\nактуальные инициативы', callback_data="look_cur")],
        [InlineKeyboardButton(text='Посмотреть\nреализованные проекты', callback_data="look_old")],
        [InlineKeyboardButton(text='Посмотреть свои инициативы', callback_data="look_my")],
        [InlineKeyboardButton(text='Выбери\nинтересующий район', callback_data="region")]
    ])

    await bot.send_message(chat_id=message.chat.id, 
                           text='Ты оказался в главном меню. Выбери что тебе по душе :)', 
                           parse_mode=ParseMode.MARKDOWN,
                           reply_markup=markup)
    
@dp.callback_query(lambda call: call.data == 'create')
async def callback_create(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    await bot.send_message(callback_query.message.chat.id, 'Отлично! Давай создадим что-то новое!')
    await bot.send_message(callback_query.message.chat.id, 'Напиши заголовок инициативы:')
    await state.set_state(IdeaForm.title)

#region

@dp.message(IdeaForm.title)
@dp.message(IdeaForm.text)
@dp.message(IdeaForm.address)
@dp.message(IdeaForm.photo)
async def process_idea_info(message: Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == IdeaForm.title:
        await state.update_data(title=message.text)
        await bot.send_message(message.chat.id, 'Напиши текст инициативы:')
        await state.set_state(IdeaForm.text)
    elif current_state == IdeaForm.text:
        await state.update_data(text=message.text)
        await bot.send_message(message.chat.id, 'Напиши адрес инициативы:')
        await state.set_state(IdeaForm.address)
    elif current_state == IdeaForm.address:
        await state.update_data(address=message.text)
        await bot.send_message(message.chat.id, 'Прикрепи фото:')
        await state.set_state(IdeaForm.photo)
    elif current_state == IdeaForm.photo:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path
        full_file_path = f"C://Users//Dasha//Pictures//{photo.file_id}.jpg"

        await bot.download_file(file_path, full_file_path)
        await state.update_data(photo=full_file_path)

        data = await state.get_data()
        bd.post_idea(message.from_user.id, data['title'], data['text'], data['address'], data['photo'])
        await state.clear()

        await bot.send_message(message.chat.id, 'Давай посмотрим что получилось:)')
        await send_final_message(message.chat.id, message.from_user.id, 'None', 0)
            
async def send_final_message(chat_id: int, user_id: int, view: str, idea_id: int):
    if view == 'None':
        idea_data = bd.last_idea(user_id)
    elif view == 'View':
        idea_data = bd.get_idea(user_id,idea_id)

    title, text, address, first_name, photo_path = (
        idea_data['title'], 
        idea_data['text'], 
        idea_data['adress'], 
        idea_data['first_name'],
        idea_data['photo_prev']
    )

    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Все отлично!', callback_data=f"ideafix_Все отлично!_None_{view}")],
        [
        InlineKeyboardButton(text='Изменить', callback_data=f"ideafix_Изменить_{idea_data['idea_id']}_{view}"),
        InlineKeyboardButton(text='Удалить', callback_data=f"ideafix_Удалить_{idea_data['idea_id']}_{view}")
        ]
    ])
    photo = FSInputFile(photo_path)
    await bot.send_photo(
        chat_id,
        photo=photo,
        caption=f"Инициатива: {title}\nСодержание: {text}\nАдрес: {address}\nИнициатор: {first_name}",
        reply_markup=markup
    )

@dp.callback_query(lambda call: call.data.startswith('ideafix_'))
async def callback_ideafix(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)
    splited=callback_query.data.split('_')
    but_name=splited[1]
    idea_id=splited[2]
    view=splited[3]
    if but_name=='Все отлично!':
        if view=='None':
            await bot.send_message(callback_query.message.chat.id, 'Инициатива успешно добавлена!\n\n'+spravka)
        elif view=='View':
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Дальше 👉', callback_data=f"go_on")],
                [InlineKeyboardButton(text='На сегодня хватит✋', callback_data=f"stop")]
            ])
            await bot.send_message(callback_query.message.chat.id, 'Инициатива успешно изменена!',reply_markup=markup)

    elif but_name=='Изменить':
        markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Изменить заголовок', callback_data=f"change_title_{idea_id}_{view}")],
        [InlineKeyboardButton(text='Изменить текст', callback_data=f"change_text_{idea_id}_{view}")],
        [InlineKeyboardButton(text='Изменить адрес', callback_data=f"change_adress_{idea_id}_{view}")],
        [InlineKeyboardButton(text='Изменить фото', callback_data=f"change_photo_{idea_id}_{view}")],
        [InlineKeyboardButton(text='Оставить как есть', callback_data=f"ideafix_Все отлично!_None_{view}")]
        ])
        await bot.send_message(callback_query.message.chat.id, 'Что вы хотите изменить?',reply_markup=markup)
    elif but_name=='Удалить':
        if view=='None':
            bd.del_idea(idea_id)
            await bot.send_message(callback_query.message.chat.id, 'Вы успешно удалили инициативу\n\n'+spravka)
        elif view=='View':
            bd.del_idea(idea_id)
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Дальше 👉', callback_data=f"go_on")],
                [InlineKeyboardButton(text='На сегодня хватит✋', callback_data=f"stop")]
            ])
            await bot.send_message(callback_query.message.chat.id, 'Вы успешно удалили инициативу',reply_markup=markup)
      
@dp.callback_query(lambda call: call.data.startswith('change_'))
async def callback_change_idea(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    splited=callback_query.data.split('_')
    change_what=splited[1]
    idea_id=splited[2]
    view=splited[3]
    await state.update_data(idea_id=idea_id)
    await state.update_data(view=view)

    if change_what=='title':
        await bot.send_message(callback_query.message.chat.id, 'Введите новый заголовок:')
        await state.set_state(ChangeIdeaState.title)
    elif change_what=='text':
        await bot.send_message(callback_query.message.chat.id, 'Введите новый текст:')
        await state.set_state(ChangeIdeaState.text)
    elif change_what=='adress':
        await bot.send_message(callback_query.message.chat.id, 'Введите новый адрес:')
        await state.set_state(ChangeIdeaState.adress)
    elif change_what=='photo':
        await bot.send_message(callback_query.message.chat.id, 'Выберете новое фото:')
        await state.set_state(ChangeIdeaState.photo)

@dp.message(ChangeIdeaState.title)
@dp.message(ChangeIdeaState.text)
@dp.message(ChangeIdeaState.adress)
@dp.message(ChangeIdeaState.photo)
async def process_change(message: Message, state: FSMContext):
    data = await state.get_data()
    idea_id = data['idea_id']
    view = data['view']
    current_state = await state.get_state()

    if current_state == ChangeIdeaState.title.state:
        bd.set_title(idea_id, message.text)
        await message.reply('Заголовок обновлен.')

        await bot.send_message(message.chat.id, 'Давай посмотрим что получилось:)')
        await send_final_message(message.chat.id, message.from_user.id,view,idea_id)
        await state.clear()

    elif current_state == ChangeIdeaState.text.state:
        bd.set_text(idea_id, message.text)
        await message.reply('Текст обновлен.') 

        await bot.send_message(message.chat.id, 'Давай посмотрим что получилось:)')
        await send_final_message(message.chat.id, message.from_user.id,view,idea_id)
        await state.clear()

    elif current_state == ChangeIdeaState.adress.state:
        bd.set_adress(idea_id, message.text)
        await message.reply('Адрес обновлен.')

        await bot.send_message(message.chat.id, 'Давай посмотрим что получилось:)')
        await send_final_message(message.chat.id, message.from_user.id,view,idea_id)
        await state.clear()

    elif current_state == ChangeIdeaState.photo.state and message.photo:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file_path = file_info.file_path
        full_file_path = f"C://Users//Dasha//Pictures//{photo.file_id}.jpg"
        await bot.download_file(file_path, full_file_path)
        bd.set_photo(idea_id, full_file_path)
        await message.reply('Фото обновлено.')
        
        await bot.send_message(message.chat.id, 'Давай посмотрим что получилось:)')
        await send_final_message(message.chat.id, message.from_user.id,view,idea_id)
        await state.clear()
    else:
        await message.reply('Пожалуйста, отправьте корректную информацию.')
    
#endregion

@dp.callback_query(lambda call: call.data == 'look_cur')
async def callback_look_cur(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.message.chat.id, 'Посмотрим, какие новые инициативы у нас есть за последнее время...\n')
    
    await state.set_state(IdeaViewing.viewing)
    await state.update_data(offset=0)
    await send_next_idea(callback_query.message.chat.id, callback_query.from_user.id, state,'new')

@dp.callback_query(lambda call: call.data == 'look_old')
async def callback_look_old(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.message.chat.id, 'Это раздел с инициативами, которые воплатились в жизнь!')
    
    await state.set_state(IdeaViewing.viewing)
    await state.update_data(offset=0)
    await send_next_idea(callback_query.message.chat.id, callback_query.from_user.id, state, 'old')

#region
async def send_next_idea(chat_id: int, user_id: int, state: FSMContext, what: str):
    state_data = await state.get_data()
    offset = state_data.get('offset', 0)
    
    region = bd.get_region(user_id)
    idea = {}
    if what=='new':
        idea = bd.cur_idea(offset,region['region'])
    elif what=='old':
        idea = bd.cur_idea(offset,region['region'],'released')

    if not idea:
        await bot.send_message(chat_id, "Инициативы закончились :(\n"+spravka)
    else:  
        firstname = bd.get_firstname(idea['idea_id'])  

        if what=='new':
            message_text = clean_message(f"""
            <b>{idea['title']}</b>
            {idea['text']}
            Адрес: {idea['adress']}
            Район: {region['region']}
            Статус: {idea['status']}
            Инициатор: {firstname['first_name']}""")

        elif what=='old':
            message_text = clean_message(f"""
            <b>{idea['title']}</b>
            {idea['text']}
            Адрес: {idea['adress']}
            Район: {region['region']}
            Статус: {idea['status']}
            Инициатор: {firstname['first_name']}
            Ответвенное лицо: {idea['master']}
            Телефон: {idea['contact']}
            """)
        
        markup = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text='Я за 👍', callback_data=f"vote_good_{idea['idea_id']}_{what}")],
            [InlineKeyboardButton(text='Я против 👎', callback_data=f"vote_bad_{idea['idea_id']}_{what}")],
            [InlineKeyboardButton(text='Не знаю 🤷‍♂️', callback_data=f"vote_pass_{idea['idea_id']}_{what}")],
            [InlineKeyboardButton(text='На сегодня хватит✋', callback_data='stop')]
        ])
        photo = FSInputFile(idea['photo'])
        await bot.send_photo(chat_id, 
                            photo=photo,
                            caption=message_text, 
                            parse_mode=ParseMode.HTML,
                            reply_markup=markup)
    
@dp.callback_query(lambda call: call.data.startswith('vote_'))  
async def handle_stop(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    splited=callback_query.data.split('_')
    idea_choice = splited[1]
    idea_id = splited[2]
    what = splited[3]

    if idea_choice == 'good':
        bd.set_votes('good_reactes',idea_id)
    elif idea_choice == 'bad':
        bd.set_votes('bad_reactes',idea_id)
    else:
        bd.set_votes('pass_reactes',idea_id)

    votes = bd.get_votes(idea_id)

    await bot.send_message(callback_query.message.chat.id,
                           f"Твой голос учтен!\nВот текущие результаты голосования: 👍{votes['good_reactes']} 👎{votes['bad_reactes']} 🤷‍♀️{votes['pass_reactes']}")
    
    state_data = await state.get_data()
    offset = state_data.get('offset', 0)

    await state.update_data(offset = offset + 1)
    await send_next_idea(callback_query.message.chat.id,callback_query.from_user.id, state, what)

@dp.callback_query(lambda call: call.data == 'stop')
async def handle_stop(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await state.clear()
    await bot.send_message(callback_query.message.chat.id, spravka)
    
#endregion
        
@dp.callback_query(lambda call: call.data == 'look_my')
async def callback_look_my(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.message.chat.id, 'Это раздел с твоими инициативами!')
    
    await state.set_state(IdeaViewing.viewing)
    await state.update_data(offset=0)
    await send_next_myidea(callback_query.message.chat.id, callback_query.from_user.id, state)

#region
async def send_next_myidea(chat_id: int, user_id: int, state: FSMContext):
    state_data = await state.get_data()
    offset = state_data.get('offset', 0)
    
    region = bd.get_region(user_id)
    idea = bd.cur_my_idea(offset,region['region'])
    if not idea:
        await bot.send_message(chat_id, "Инициативы закончились :(\n"+spravka)
    else:  
        message_text = clean_message(f"""
            <b>{idea['title']}</b>
            {idea['text']}
            Адрес: {idea['adress']}
            Район: {region['region']}
            Статус: {idea['status']}
            Ответвенное лицо: {idea['master']}
            Телефон: {idea['contact']}
            Результаты голосования: 👍{idea['good_reactes']} 👎{idea['bad_reactes']} 🤷‍♀️{idea['pass_reactes']}
            """)
        if idea['status']=='in processing':
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [
                InlineKeyboardButton(text='Изменить', callback_data=f"ideafix_Изменить_{idea['idea_id']}_View"),
                InlineKeyboardButton(text='Удалить', callback_data=f"ideafix_Удалить_{idea['idea_id']}_View")
                ],
                [InlineKeyboardButton(text='Дальше 👉', callback_data=f"go_on")],
                [InlineKeyboardButton(text='На сегодня хватит✋', callback_data=f"stop")]
            ])
        else:
            markup = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Дальше 👉', callback_data=f"go_on")],
                [InlineKeyboardButton(text='На сегодня хватит✋', callback_data=f"stop")],
            ])
        photo = FSInputFile(idea['photo'])
        await bot.send_photo(chat_id, 
                            photo=photo,
                            caption=message_text, 
                            parse_mode=ParseMode.HTML,
                            reply_markup=markup)
        
@dp.callback_query(lambda call: call.data == 'go_on')  
async def handle_stop(callback_query: CallbackQuery, state: FSMContext):
    await bot.answer_callback_query(callback_query.id)

    state_data = await state.get_data()
    offset = state_data.get('offset', 0)

    await state.update_data(offset = offset + 1)
    await send_next_myidea(callback_query.message.chat.id,callback_query.from_user.id, state)
#endregion

@dp.callback_query(lambda call: call.data == 'region')
async def callback_region(callback_query: CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Вахитовский район', callback_data="region_Вахитовский")],
        [InlineKeyboardButton(text='Авиастроительный район', callback_data="region_Авиастроительный")],
        [InlineKeyboardButton(text='Кировский район', callback_data="region_Кировский")],
        [InlineKeyboardButton(text='Московский район', callback_data="region_Московский")],
        [InlineKeyboardButton(text='Ново-Савиновский район', callback_data="region_Ново-Савиновский")],
        [InlineKeyboardButton(text='Советский район', callback_data="region_Советский")],
        [InlineKeyboardButton(text='Приволжский район', callback_data="region_Приволжский")],
        [InlineKeyboardButton(text='Все районы', callback_data="region_Все районы")]
    ])
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(callback_query.message.chat.id,
                            text=f'''Это список районов твоего города.\nВ зависимости от твоего выбора тебе будут предложены инициативы из соответвующего района или даже всего города!''',
                            parse_mode=ParseMode.MARKDOWN,
                            reply_markup=markup)

#region
@dp.callback_query(lambda call: call.data.startswith('region_'))
async def call_back_region(callback_query: CallbackQuery):
    await bot.answer_callback_query(callback_query.id)

    region_name=callback_query.data.split('_')[1]
    if region_name=='Все районы':
        await bot.send_message(callback_query.message.chat.id, 'Принято! Теперь вы интересуетесь всеми районами!')
        bd.set_region(callback_query.from_user.id,str(region_name))
    else:
        await bot.send_message(callback_query.message.chat.id, f'Принято! Теперь вы интересуетесь районом "{region_name}."')
        bd.set_region(callback_query.from_user.id,str(region_name))
    await bot.send_message(callback_query.message.chat.id, spravka)
#endregion

def clean_message(text):
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    return "\n".join(lines)

if __name__ == "__main__":
    dp.run_polling(bot)
