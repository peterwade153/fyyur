from app import db, Genre


def add_genres():
    genres_list = [
        'Alternative',
        'Blues',
        'Classical',
        'Country',
        'Electronic',
        'Folk',
        'Funk',
        'Hip-Hop',
        'Heavy Metal',
        'Instrumental',
        'Jazz',
        'Musical Theatre',
        'Pop',
        'Punk',
        'R&B',
        'Reggae',
        'Rock n Roll',
        'Soul',
        'Other'
    ]

    for genre in genres_list:
        db.session.add(Genre(name=genre))
        db.session.commit()
    return


if __name__ == '__main__':
    add_genres()
